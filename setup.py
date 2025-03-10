#!/usr/bin/env python3
"""Setup the Noun Project MCP server development environment."""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Set up the development environment using uv."""
    script_dir = Path(__file__).parent
    
    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: uv is not installed or not in your PATH", file=sys.stderr)
        print("Please install uv from https://github.com/astral-sh/uv", file=sys.stderr)
        sys.exit(1)
    
    # Install the package in development mode
    print("Installing development dependencies...")
    try:
        subprocess.run(["uv", "pip", "install", "-e", "."], check=True)
        print("Development environment setup complete!")
        print()
        print("Next steps:")
        print("1. Edit the .env file to add your Noun Project API credentials")
        print("2. Run ./dev.py to start the server in development mode")
        print("3. Run ./install.py to install the server in Claude Desktop")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up development environment: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()