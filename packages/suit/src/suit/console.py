from rich.console import Console
import os

console = Console(
    log_path=False,
    width=int(os.environ["SUIT_SCREEN_WIDTH"]) if "SUIT_SCREEN_WIDTH" in os.environ else None,
)
