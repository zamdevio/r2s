"""Command history service for interactive shell."""

from typing import List, Optional
from pathlib import Path


class CommandHistory:
    """Manage command history for interactive shell."""
    
    def __init__(self, max_size: int = 1000, history_file: Optional[str] = None):
        self.max_size = max_size
        self.history: List[str] = []
        self.current_index = -1
        
        # Default history file location
        if history_file is None:
            from ..utils.helpers import get_r2s_home
            r2s_home = get_r2s_home()
            self.history_file = r2s_home / "history"
        else:
            if isinstance(history_file, str) and history_file.startswith("~"):
                self.history_file = Path(history_file).expanduser()
            else:
                self.history_file = Path(history_file)
        
        # Load history from file
        self.load()
    
    def add(self, command: str):
        """Add command to history."""
        if command.strip() and (not self.history or self.history[-1] != command.strip()):
            self.history.append(command.strip())
            if len(self.history) > self.max_size:
                self.history.pop(0)
            self.current_index = len(self.history)
            self.save()
    
    def get_previous(self) -> Optional[str]:
        """Get previous command in history."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        elif self.current_index == 0:
            return self.history[0]
        return None
    
    def get_next(self) -> Optional[str]:
        """Get next command in history."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        elif self.current_index == len(self.history) - 1:
            self.current_index = len(self.history)
            return None
        return None
    
    def reset_index(self):
        """Reset history index to end."""
        self.current_index = len(self.history)
    
    def load(self):
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = [line.strip() for line in f if line.strip()]
                self.current_index = len(self.history)
            except Exception:
                self.history = []
    
    def save(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for cmd in self.history:
                    f.write(cmd + '\n')
        except Exception:
            pass  # Fail silently
    
    def clear(self):
        """Clear history."""
        self.history = []
        self.current_index = -1
        if self.history_file.exists():
            try:
                self.history_file.unlink()
            except Exception:
                pass
    
    def get_all(self) -> List[str]:
        """Get all history."""
        return self.history.copy()

