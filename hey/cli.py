"""CLI configuration interface for hey."""
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
import sys

from .config import Config, Model, load_config
from .memory import get_cache

console = Console()

def configure_model(config: Config) -> None:
    """Configure the AI model."""
    models = [Choice(model.value, model.value) for model in Model]
    current_model = next((i for i, m in enumerate(models) if m.value == config.model), 0)
    models.append(Choice(None, "other..."))

    model = inquirer.select(
        message="Select AI Model:",
        choices=models,
        default=models[current_model],
        qmark="🤖",
    ).execute()

    if not model:
        model = inquirer.text(
            message="Enter model name:",
            qmark="🤖",
        ).execute()

    config.model = model
    console.print(f"[green]Model set to: {config.model}[/]")

def configure_prompt(config: Config) -> None:
    """Configure the system prompt."""
    console.print("Current prompt:", "[cyan]" + (config.prompt or "Not set") + "[/]")

    set_prompt = inquirer.confirm(
        message="Would you like to set a new system prompt?",
        default=False,
        qmark="💭",
    ).execute()

    if set_prompt:
        prompt = inquirer.text(
            message="Enter new system prompt (press Enter to clear):",
            qmark="📝",
        ).execute()

        config.prompt = prompt if prompt else None
        if config.prompt:
            console.print(f"[green]System prompt set to: {config.prompt}[/]")
        else:
            console.print("[yellow]System prompt cleared[/]")

def configure_proxy(config: Config) -> None:
    """Configure proxy settings."""
    console.print("Current HTTP proxy:", "[cyan]" + (config.proxy or "Not set") + "[/]")
    console.print("Current SOCKS proxy:", "[cyan]" + (config.socks_proxy or "Not set") + "[/]")

    # Configure HTTP proxy
    configure_http = inquirer.confirm(
        message="Would you like to configure HTTP proxy?",
        default=False,
        qmark="🌐",
    ).execute()

    if configure_http:
        proxy = inquirer.text(
            message="Enter HTTP proxy URL (e.g., http://proxy:8080) or press Enter to clear:",
            qmark="🔗",
        ).execute()

        if proxy:
            if config.validate_proxy_url(proxy):
                config.proxy = proxy
                console.print(f"[green]HTTP proxy set to: {proxy}[/]")
            else:
                console.print("[red]Invalid HTTP proxy URL format[/]")
        else:
            config.proxy = None
            console.print("[yellow]HTTP proxy cleared[/]")

    # Configure SOCKS proxy
    configure_socks = inquirer.confirm(
        message="Would you like to configure SOCKS proxy?",
        default=False,
        qmark="🧦",
    ).execute()

    if configure_socks:
        proxy = inquirer.text(
            message="Enter SOCKS proxy URL (e.g., socks5://proxy:1080) or press Enter to clear:",
            qmark="🔗",
        ).execute()

        if proxy:
            if config.validate_proxy_url(proxy, allow_socks=True):
                config.socks_proxy = proxy
                console.print(f"[green]SOCKS proxy set to: {proxy}[/]")
            else:
                console.print("[red]Invalid SOCKS proxy URL format[/]")
        else:
            config.socks_proxy = None
            console.print("[yellow]SOCKS proxy cleared[/]")

def configure_tos(config: Config) -> None:
    """Configure Terms of Service acceptance."""
    if not config.tos:
        console.print("[bold red]Terms of Service[/]")
        console.print("You must agree to DuckDuckGo's Terms of Service to use this tool.")
        console.print("Read them here: [link]https://duckduckgo.com/terms[/]")

        agree = inquirer.confirm(
            message="Do you agree to the Terms of Service?",
            default=False,
            qmark="📜",
        ).execute()

        if agree:
            config.tos = True
            console.print("[green]Terms of Service accepted[/]")
    else:
        console.print("[green]✓ Terms of Service already accepted[/]")

def run_config() -> None:
    """Run the configuration interface."""
    config = load_config()
    if not config:
        config = Config()

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        cache = get_cache()
        cache.clear()
        console.print("[green]Message cache cleared![/]")
        return

    # Show current settings
    console.print("[bold blue]Current Settings:[/]")
    console.print(f"Model: [cyan]{config.model}[/]")
    console.print(f"Terms of Service: [cyan]{'Accepted' if config.tos else 'Not Accepted'}[/]")
    console.print(f"System Prompt: [cyan]{config.prompt or 'Not set'}[/]")
    console.print(f"HTTP Proxy: [cyan]{config.proxy or 'Not set'}[/]")
    console.print(f"SOCKS Proxy: [cyan]{config.socks_proxy or 'Not set'}[/]")
    console.print()

    # Configure each setting
    configure_tos(config)
    configure_model(config)
    configure_prompt(config)
    configure_proxy(config)

    # Save configuration
    if inquirer.confirm(
        message="Save changes?",
        default=True,
        qmark="💾",
    ).execute():
        config.save()
        console.print("[green]Configuration saved successfully![/]")
    else:
        console.print("[yellow]Changes discarded[/]")


if __name__ == "__main__":
    run_config()
