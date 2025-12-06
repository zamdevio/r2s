"""Color utilities for terminal output."""


class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    BROWN = "\033[38;5;130m"
    COFFEE = "\033[38;5;94m"
    
    # Extended colors
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_MAGENTA = "\033[95m"
    
    # 256-color palette
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;129m"
    PINK = "\033[38;5;213m"
    LIME = "\033[38;5;118m"
    TEAL = "\033[38;5;43m"
    
    # Styles
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"


def colorize(text: str, color: str) -> str:
    """Apply color to text."""
    return f"{color}{text}{Colors.RESET}"


def disable_colors():
    """Disable all colors."""
    Colors.RED = ""
    Colors.GREEN = ""
    Colors.YELLOW = ""
    Colors.BLUE = ""
    Colors.MAGENTA = ""
    Colors.CYAN = ""
    Colors.WHITE = ""
    Colors.BOLD = ""
    Colors.RESET = ""
    Colors.BROWN = ""
    Colors.COFFEE = ""
    Colors.BRIGHT_CYAN = ""
    Colors.BRIGHT_BLUE = ""
    Colors.BRIGHT_GREEN = ""
    Colors.BRIGHT_YELLOW = ""
    Colors.BRIGHT_RED = ""
    Colors.BRIGHT_MAGENTA = ""
    Colors.ORANGE = ""
    Colors.PURPLE = ""
    Colors.PINK = ""
    Colors.LIME = ""
    Colors.TEAL = ""
    Colors.DIM = ""
    Colors.ITALIC = ""
    Colors.UNDERLINE = ""
    Colors.BLINK = ""
    Colors.REVERSE = ""

