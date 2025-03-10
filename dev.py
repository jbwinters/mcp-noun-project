#!/usr/bin/env python3
"""Run the Noun Project MCP server in development mode."""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Run the MCP server in development mode with the MCP Inspector."""
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "mcp_noun_project" / "server.py"
    
    # Verify the server file exists
    if not server_path.exists():
        print(f"Error: Server file not found at {server_path}", file=sys.stderr)
        sys.exit(1)
    
    # Check for API credentials
    env_file = script_dir / ".env"
    if not env_file.exists():
        print("Error: .env file not found", file=sys.stderr)
        print("Please create a .env file with your Noun Project API credentials", file=sys.stderr)
        sys.exit(1)
    
    # Load environment variables
    load_dotenv(env_file)
    api_key = os.environ.get("NOUN_PROJECT_API_KEY")
    api_secret = os.environ.get("NOUN_PROJECT_API_SECRET")
    
    if not api_key or api_key == "your_api_key" or not api_secret or api_secret == "your_api_secret":
        print("Error: Invalid API credentials in .env file", file=sys.stderr)
        print("Please update your .env file with valid Noun Project API credentials:", file=sys.stderr)
        print("NOUN_PROJECT_API_KEY=your_actual_api_key", file=sys.stderr)
        print("NOUN_PROJECT_API_SECRET=your_actual_api_secret", file=sys.stderr)
        print("\nYou can get API credentials from https://thenounproject.com/developers/", file=sys.stderr)
        sys.exit(1)
    
    print("API credentials found in .env file")
    
    # Build the dev command
    cmd = ["mcp", "dev", str(server_path)]
    
    # Add dependencies
    cmd.extend(["--with", "httpx", "--with", "python-dotenv"])
    
    # Add editable package
    cmd.extend(["--with-editable", "."])
    
    # Run the command
    try:
        print("Starting MCP server in development mode...")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running MCP server in development mode: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Development server stopped by user")

if __name__ == "__main__":
    main()