#!/usr/bin/env python3
"""
Entry point for r2s binary - handles PyInstaller packaging
"""
import sys
import os

# Add the parent directory to path so we can import react2shell
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    # PyInstaller sets sys._MEIPASS to the temp folder
    base_path = sys._MEIPASS
    # Add the base path to sys.path
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
else:
    # Running as script - add parent directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

# Now import and run the main module
from react2shell.main import main

if __name__ == "__main__":
    main()

