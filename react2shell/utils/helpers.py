"""Helper functions for React2Shell."""

import re
import base64
import os
from pathlib import Path
from urllib.parse import unquote
from typing import Optional


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from text (for reports)."""
    if not text:
        return text
    
    # Remove all ANSI escape sequences
    # Pattern: \x1b[ or \033[ followed by numbers, semicolons, and ending with a letter
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\[[0-9;]*m|\033\[[0-9;]*[a-zA-Z]|\033\[[0-9;]*m')
    text = ansi_escape.sub('', text)
    
    # Also remove common color codes like [93m, [0m, etc. (what shows in reports)
    text = re.sub(r'\[[0-9;]+m', '', text)
    
    return text


def get_r2s_home() -> Path:
    """Get the R2S home directory (~/.r2s)."""
    home = Path.home()
    r2s_home = home / ".r2s"
    r2s_home.mkdir(exist_ok=True)
    return r2s_home


def extract_result_from_redirect(response, base64_encoded: bool = True) -> Optional[str]:
    """Extract command result from redirect response."""
    redirect_header = response.headers.get("X-Action-Redirect", "")
    location_header = response.headers.get("Location", "")
    
    # Try to extract result from redirect URL (handle both /login?a= and login?a= patterns)
    for header in [redirect_header, location_header]:
        if header:
            # Try multiple patterns to catch different redirect formats
            patterns = [
                r'/login\?a=([^;&\s]+)',  # /login?a=...
                r'login\?a=([^;&\s]+)',   # login?a=... (without leading slash)
                r'[?&]a=([^;&\s]+)',      # Any ?a= or &a= parameter
            ]
            for pattern in patterns:
                match = re.search(pattern, header)
                if match:
                    result = match.group(1)
                    # URL decode
                    try:
                        decoded = unquote(result)
                        # Try to base64 decode if it looks like base64
                        if base64_encoded:
                            try:
                                decoded_bytes = base64.b64decode(decoded)
                                return decoded_bytes.decode('utf-8', errors='replace')
                            except:
                                # Not base64, return as-is
                                return decoded
                        return decoded
                    except:
                        return result
    return None


def print_banner():
    """Print the tool banner with ASCII art, developer info, and timestamp."""
    from .colors import Colors
    from datetime import datetime
    import re
    
    # Get current timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%A, %B %d, %Y")
    
    # ASCII art logo for React2Shell
    box_width = 67
    
    # Calculate padding for centered/left-aligned text
    def format_line(text, dim_prefix="", color=""):
        """Format a line with proper padding to match box width."""
        # Remove ANSI codes for length calculation
        clean_text = re.sub(r'\033\[[0-9;]*[a-zA-Z]', '', text)
        clean_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', clean_text)
        text_len = len(clean_text)
        padding = box_width - text_len - 4  # Account for "║  " and "  ║"
        return f"    ║{dim_prefix}{text}{' ' * padding}{color}  ║"
    dev_text = f"  Developer: {Colors.BRIGHT_CYAN}https://github.com/zamdevio{Colors.RESET}"
    time_text = f"  Started: {Colors.BRIGHT_GREEN}{timestamp}{Colors.RESET}"
    date_text = f"  Date: {Colors.BRIGHT_GREEN}{date_str}{Colors.RESET}"
    
    ascii_logo = f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}
    ██████╗ ███████╗ ██████╗ ████████╗    ███████╗██╗  ██╗███████╗██╗     ██╗     
    ██╔══██╗██╔════╝██╔═══██╗╚══██╔══╝    ██╔════╝██║  ██║██╔════╝██║     ██║     
    ██████╔╝█████╗  ██║   ██║   ██║       ███████╗███████║█████╗  ██║     ██║     
    ██╔══██╗██╔══╝  ██║   ██║   ██║       ╚════██║██╔══██║██╔══╝  ██║     ██║     
    ██║  ██║███████╗╚██████╔╝   ██║       ███████║██║  ██║███████╗███████╗███████╗
    ╚═╝  ╚═╝╚══════╝ ╚═════╝    ╚═╝       ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
{Colors.RESET}
{Colors.BRIGHT_BLUE}{Colors.BOLD}    ╔{'═' * (box_width - 2)}╗
    ║{Colors.BRIGHT_CYAN}  React2Shell (R2S) - CVE-2025-55182 Exploitation Framework{Colors.BRIGHT_BLUE}      ║
    ║{Colors.TEAL}  Advanced Security Testing & Command Execution Tool{Colors.BRIGHT_BLUE}             ║
    ║{Colors.BRIGHT_BLUE}                                                                 ║
{format_line(dev_text, Colors.DIM, Colors.BRIGHT_BLUE)}
{format_line(time_text, Colors.DIM, Colors.BRIGHT_BLUE)}
{format_line(date_text, Colors.DIM, Colors.BRIGHT_BLUE)}
    ╚{'═' * (box_width - 2)}╝{Colors.RESET}
"""
    print(ascii_logo)


def print_section_header(title: str):
    """Print a section header with enhanced styling matching the banner."""
    from .colors import Colors
    
    # Calculate padding for centered title (matching banner width: 67 chars)
    # Banner format: "║  " (3 chars) + content + padding + "  ║" (3 chars) = 67
    # So: content + padding = 67 - 6 = 61
    box_width = 67
    title_len = len(title)
    available_space = box_width - 6  # Account for "║  " and "  ║"
    padding_left = (available_space - title_len) // 2
    padding_right = available_space - title_len - padding_left
    
    # Create decorative header matching banner style exactly
    header = f"""
{Colors.BRIGHT_BLUE}{Colors.BOLD}    ╔{'═' * (box_width - 2)}╗
    ║{Colors.BRIGHT_CYAN}  {' ' * padding_left}{Colors.BOLD}{title}{Colors.BRIGHT_BLUE}{' ' * padding_right}  ║
    ╚{'═' * (box_width - 2)}╝{Colors.RESET}
"""
    print(header)

