"""Logging service for React2Shell."""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class R2SLogger:
    """Logger for React2Shell operations."""
    
    def __init__(self, log_file: Optional[str] = None, level: str = "INFO"):
        self.log_file = log_file
        self.enabled = log_file is not None
        
        if self.enabled:
            # Create logs directory if needed
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup logger
            self.logger = logging.getLogger('r2s')
            self.logger.setLevel(getattr(logging, level.upper()))
            
            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Format
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        else:
            self.logger = None
    
    def log(self, level: str, message: str, **kwargs):
        """Log a message."""
        if not self.enabled or not self.logger:
            return
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_message = message
        if kwargs:
            log_message += f" | {kwargs}"
        log_method(log_message)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log("INFO", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log("DEBUG", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log("ERROR", message, **kwargs)
    
    def command(self, command: str, target: str, result: dict):
        """Log command execution."""
        if self.enabled:
            status = "SUCCESS" if result.get("success") else "FAILED"
            self.info(f"Command: {command} | Target: {target} | Status: {status}", 
                     status_code=result.get("status_code"),
                     error=result.get("error"))

