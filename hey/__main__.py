"""Main entry point for the hey CLI."""
import os
import sys
import time
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import api
from .config import Config, load_config
from .cli import run_config


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('--agree-tos', is_flag=True, help='Agree to the DuckDuckGo TOS')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--prompt', '-p', help='Set a system prompt for all responses')
@click.option('--save-prompt', is_flag=True, help='Save the provided prompt to config')
@click.option('--proxy', help='HTTP/HTTPS proxy URL (e.g., http://proxy:8080)')
@click.option('--socks-proxy', help='SOCKS proxy URL (e.g., socks5://proxy:1080)')
@click.argument('args', nargs=-1)
def cli(args: tuple[str, ...], agree_tos: bool, verbose: bool, prompt: str | None,
        save_prompt: bool, proxy: str | None, socks_proxy: str | None) -> None:
    """Hey - DuckDuckGo Chat CLI.

    Examples:
        hey "What is Python?"
        hey how are you
        hey --prompt "You are a Python expert" "How do I use decorators?"
        hey -v "Tell me about asyncio"
        hey --proxy http://proxy:8080 "What's my IP?"
        hey --socks-proxy socks5://proxy:1080 "What's my IP?"

        # Configure settings
        hey config
    """
    if len(args) == 1 and args[0] == "config":
        run_config()
        return

    config = load_config()
    if not config:
        config = Config()

    if agree_tos:
        if not config.tos:
            print("\033[32mTOS accepted\033[0m")
        config.tos = True
        config.save()

    if prompt:
        config.prompt = prompt
        if save_prompt:
            config.save()
            print(f"\033[32mSaved system prompt to config\033[0m")

    if proxy:
        if not config.validate_proxy_url(proxy):
            print(f"\033[31mInvalid HTTP proxy URL format: {proxy}\033[0m", file=sys.stderr)
            sys.exit(1)
        config.proxy = proxy
        if save_prompt:
            config.save()
            print(f"\033[32mSaved proxy settings to config\033[0m")

    if socks_proxy:
        if not config.validate_proxy_url(socks_proxy, allow_socks=True):
            print(f"\033[31mInvalid SOCKS proxy URL format: {socks_proxy}\033[0m", file=sys.stderr)
            sys.exit(1)
        config.socks_proxy = socks_proxy
        if save_prompt:
            config.save()
            print(f"\033[32mSaved proxy settings to config\033[0m")

    config.verbose = verbose

    if not config.tos:
        print("\033[31mYou must agree to DuckDuckGo's Terms of Service to use this tool.\033[0m", file=sys.stderr)
        print("Read them here: https://duckduckgo.com/terms", file=sys.stderr)
        print("Once you read it, pass --agree-tos parameter to agree.", file=sys.stderr)
        print(f"\033[33mNote: if you want to, modify `tos` parameter in {Path(Config.get_path()) / Config.get_file_name()}\033[0m",
              file=sys.stderr)
        sys.exit(3)

    if not sys.stdout.isatty():
        print("This program must be run in a terminal", file=sys.stderr)
        sys.exit(1)

    query_str = ' '.join(args)
    if not query_str:
        print("Please provide a query", file=sys.stderr)
        sys.exit(1)

    proxies = config.get_proxies()

    client = httpx.Client(
        transport=httpx.HTTPTransport(retries=2),
        verify=True,
        follow_redirects=True,
        timeout=30.0,
        proxies=proxies or None
    )

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Initializing...[/]"),
            transient=True,  # Remove progress bar when done
            console=Console(stderr=True)  # Show on stderr to not interfere with response
        ) as progress:
            task = progress.add_task("", total=None)  # Indeterminate progress

            progress.update(task, description="[bold blue]Getting verification token...[/]")
            vqd = api.get_vqd(client, config)

            progress.update(task, description="[bold blue]Connecting to DuckDuckGo...[/]")
            api.get_response(client, query_str, vqd, config)

    except Exception as e:
        print(f"\033[31mError: {str(e)}\033[0m", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == '__main__':
    cli()
