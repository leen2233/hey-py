"""DuckDuckGo Chat API client implementation."""
import json
import sys
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.screen import Screen

from .config import Config
from .memory import get_cache
from .models import ChatMessage, ChatPayload


@dataclass
class ChatChunk:
    """Chat response chunk structure."""
    role: Optional[str]
    message: str
    created: int
    action: str
    id: Optional[str]
    model: Optional[str]


@dataclass
class ErrorChatChunk:
    """Error response chunk structure."""
    action: str
    status: int
    err_type: str


def log_debug(msg: str, verbose: bool = False) -> None:
    """Print debug message with timestamp."""
    if verbose:
        print(f"\033[36m[{time.strftime('%H:%M:%S')}] {msg}\033[0m", file=sys.stderr)


def get_headers() -> Dict[str, str]:
    """Get the required headers for API requests."""
    return {
        "Host": "duckduckgo.com",
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": "ax=v309-3",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }


def simulate_browser_reqs(client: httpx.Client, config: Config) -> None:
    """Simulate browser requests to avoid detection."""
    log_debug("Browser simulation disabled for better performance with proxies", config.verbose)
    return


def get_vqd(client: httpx.Client, config: Config) -> str:
    """Get the VQD token required for chat requests."""
    simulate_browser_reqs(client, config)

    log_debug("Requesting VQD token...", config.verbose)
    headers = get_headers()
    headers.update({
        "Cache-Control": "no-store",
        "x-vqd-accept": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    })

    response = client.get(
        "https://duckduckgo.com/duckchat/v1/status",
        headers=headers,
        follow_redirects=True,
        timeout=10.0
    )

    vqd = response.headers.get("x-vqd-4")
    if not vqd:
        raise ValueError("No VQD header returned")
    log_debug(f"Got VQD token: {vqd[:8]}...", config.verbose)
    return vqd


def get_response(client: httpx.Client, query: str, vqd: str, config: Config) -> None:
    """Get chat response from DuckDuckGo."""
    cache = get_cache()

    user_message = ChatMessage(role="user", content=f"my question: {query}")
    cache.add_message(user_message)

    # prepare chat history
    messages = cache.get_messages()

    payload = ChatPayload(
        model=config.model,
        messages=messages,
    )

    # convert dataclass to dictionary for serialization
    payload_dict = {
        "model": payload.model,
        "messages": [
            {"role": msg.role, "content": msg.content}
            for msg in payload.messages
        ],
    }

    # get headers and add needed headers
    headers = get_headers()
    headers.update({
        "Content-Type": "application/json",
        "x-vqd-4": vqd,
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://duckduckgo.com/?q=duckduckgo+ai+chat&ia=chat",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Origin": "https://duckduckgo.com",
    })

    log_debug("Sending chat request...", config.verbose)
    start_time = time.time()

    with client.stream(
        "POST",
        "https://duckduckgo.com/duckchat/v1/chat",
        headers=headers,
        json=payload_dict,
        timeout=30.0
    ) as response:
        log_debug(f"Got initial response in {time.time() - start_time:.2f}s", config.verbose)

        new_vqd = response.headers.get("x-vqd-4")
        if new_vqd:
            log_debug(f"Got new VQD token: {new_vqd[:8]}...", config.verbose)
        else:
            print("\033[33mWarn: DuckDuckGo did not return new VQD. Ignore this if everything else is ok.\033[0m",
                  file=sys.stderr)

        console = Console()
        current_response = ""

        log_debug("Starting response stream...", config.verbose)
        # live display
        with Live(Markdown(current_response), console=console, refresh_per_second=4) as live:
            chunk_count = 0
            last_update = time.time()
            complete_response = ""

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    chunk = line.replace("data: ", "")
                    data = json.loads(chunk)

                    if data.get("action") == "error":
                        print(f"\033[31mError obtaining response: {data.get('status')} - {data.get('type')}\033[0m",
                              file=sys.stderr)
                        sys.exit(1)

                    if "message" in data:
                        chunk_count += 1
                        if time.time() - last_update >= 1.0:  # Log every second
                            log_debug(f"Received {chunk_count} chunks...", config.verbose)
                            last_update = time.time()

                        message = data["message"]
                        current_response += message
                        complete_response += message
                        live.update(Markdown(current_response))

                except json.JSONDecodeError:
                    continue

        log_debug("Response complete", config.verbose)

        if complete_response and not data.get("action") == "error":
            assistant_message = ChatMessage(role="user", content=f"your answer: {complete_response}")
            cache.add_message(assistant_message)
