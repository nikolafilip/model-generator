#!/usr/bin/env python3
"""
3D Divider Generator - Main application

This module contains the entry point for the 3D Divider Generator application.
"""
import os
import sys
import logging
import tkinter as tk

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for the application."""
    setup_logging()
    
    # Get the project root directory (one level up from the src directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Ensure exports directory exists
    exports_dir = os.path.join(project_root, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("3D Divider Generator")
    
    # Create the main application window
    app = MainWindow(root, project_root)
    
    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()
