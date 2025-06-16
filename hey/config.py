"""Configuration management for hey."""
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import toml


class Model(Enum):
    """Available chat models."""
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"  # Default model
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_O4_MINI = "o4-mini"
    LLAMA_3_3_70B = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    MISTRAL_24B = "mistralai/Mistral-Small-24B-Instruct-2501"


@dataclass
class Config:
    """Configuration data."""
    tos: bool = False
    model: str = Model.CLAUDE_3_HAIKU.value
    prompt: Optional[str] = None  # System prompt to apply to all responses
    verbose: bool = False  # Whether to show debug logs
    proxy: Optional[str] = None  # HTTP/HTTPS proxy URL
    socks_proxy: Optional[str] = None  # SOCKS proxy URL

    @staticmethod
    def get_path() -> str:
        """Get the config directory path."""
        return os.getenv("HEY_CONFIG_PATH", os.path.expanduser("~/.config/hey"))

    @staticmethod
    def get_file_name() -> str:
        """Get the config file name."""
        return os.getenv("HEY_CONFIG_FILENAME", "conf.toml")

    def save(self) -> None:
        """Save configuration to file."""
        config_path = Path(self.get_path())
        config_path.mkdir(parents=True, exist_ok=True)

        config_file = config_path / self.get_file_name()
        config_data = {
            "tos": self.tos,
            "model": self.model,
        }

        # Only save optional fields if they're set
        if self.prompt is not None:
            config_data["prompt"] = self.prompt
        if self.proxy is not None:
            config_data["proxy"] = self.proxy
        if self.socks_proxy is not None:
            config_data["socks_proxy"] = self.socks_proxy

        with open(config_file, "w") as f:
            toml.dump(config_data, f)

    def get_proxies(self) -> dict[str, str]:
        """Get proxy configuration as a dictionary for httpx."""
        proxies = {}

        # Check environment variables first
        env_http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        env_https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        env_socks_proxy = os.getenv("SOCKS_PROXY") or os.getenv("socks_proxy")

        # Then check config values (they override environment variables)
        if self.proxy:
            proxies["http://"] = self.proxy
            proxies["https://"] = self.proxy
        elif env_http_proxy or env_https_proxy:
            if env_http_proxy:
                proxies["http://"] = env_http_proxy
            if env_https_proxy:
                proxies["https://"] = env_https_proxy

        if self.socks_proxy:
            proxies["all://"] = self.socks_proxy
        elif env_socks_proxy:
            proxies["all://"] = env_socks_proxy

        return proxies

    def validate_proxy_url(self, url: str, allow_socks: bool = False) -> bool:
        """Validate a proxy URL format."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if allow_socks:
                return parsed.scheme in ("http", "https", "socks4", "socks5")
            return parsed.scheme in ("http", "https")
        except Exception:
            return False


def load_config() -> Config:
    """Load configuration from file."""
    config = Config()
    config_file = Path(config.get_path()) / config.get_file_name()

    if config_file.exists():
        try:
            data = toml.load(config_file)
            config.tos = data.get("tos", config.tos)
            config.model = data.get("model", config.model)
            config.prompt = data.get("prompt")  # Will be None if not in file
            config.proxy = data.get("proxy")  # Will be None if not in file
            config.socks_proxy = data.get("socks_proxy")  # Will be None if not in file
        except Exception:
            # If there's any error loading the config, use defaults
            pass

    return config
