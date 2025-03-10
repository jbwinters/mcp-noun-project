#!/usr/bin/env python3
"""Test the Noun Project API client and MCP server."""

import asyncio
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_noun_project.client import NounProjectClient


async def test_client():
    """Test direct API client operations."""
    print("\n=== Testing Noun Project API Client ===")
    client = NounProjectClient()
    
    # Test search
    print("\nSearching for icons...")
    query = "cat"
    search_result = await client.search_icons(query=query, limit=5)
    
    icons = search_result.get("icons", [])
    print(f"Found {len(icons)} icons for query '{query}'")
    
    if icons:
        icon = icons[0]
        icon_id = icon.get("id")
        print(f"\nFirst result (ID: {icon_id}):")
        for key, value in icon.items():
            if key not in ["svg", "svg_url"]:  # Skip SVG data for readability
                print(f"  {key}: {value}")
        
        # Test get icon by ID
        print(f"\nGetting icon details for ID: {icon_id}")
        icon_result = await client.get_icon_by_id(icon_id=icon_id)
        icon_details = icon_result.get("icon", {})
        print(f"Retrieved icon: {icon_details.get('name')}")
        
        # Test getting download URL
        print(f"\nGetting download URL for icon: {icon_id}")
        download_url = await client.get_icon_download_url(icon_id=icon_id, size=200)
        print(f"Download URL: {download_url}")
    
    # Test autocomplete
    print("\nTesting autocomplete...")
    autocomplete_result = await client.autocomplete(query="ca", limit=5)
    suggestions = autocomplete_result.get("suggestions", [])
    print(f"Found {len(suggestions)} autocomplete suggestions for 'ca':")
    for suggestion in suggestions:
        print(f"  {suggestion.get('term')}")
    
    # Test API usage
    print("\nGetting API usage information...")
    usage_result = await client.get_usage()
    usage = usage_result.get("usage", {})
    print(f"API usage: {usage}")


async def test_mcp_server():
    """Test the MCP server functionality."""
    try:
        print("\n=== Testing MCP Server ===")
        test_dir = Path(__file__).parent / "test_mcp_server"
        os.makedirs(test_dir, exist_ok=True)
        
        # Import the functions directly
        from src.mcp_noun_project.server import (
            download_icon_as_image,
            download_icon_to_file,
            search_and_download_icons
        )
        
        # Create a mock context
        class MockContext:
            def __init__(self):
                from src.mcp_noun_project.client import NounProjectClient
                from src.mcp_noun_project.server import ServerContext
                self.request_context = type('obj', (object,), {
                    'lifespan_context': ServerContext(client=NounProjectClient())
                })
            
            def info(self, msg):
                print(f"INFO: {msg}")
            
            def warning(self, msg):
                print(f"WARNING: {msg}")
            
            def error(self, msg):
                print(f"ERROR: {msg}")
        
        # Create a context
        ctx = MockContext()
        
        # Test the download_icon_to_file function
        print("\nTesting download_icon_to_file...")
        try:
            icon_path = await download_icon_to_file(
                icon_id=5518010,
                output_path=str(test_dir / "test_icon.png"),
                color="4169E1",
                size=400,
                ctx=ctx
            )
            print(f"Downloaded icon to: {icon_path}")
        except Exception as e:
            print(f"Error in download_icon_to_file: {str(e)}")
            traceback.print_exc()
        
        # Test the download_icon_as_image function
        print("\nTesting download_icon_as_image...")
        try:
            image_content = await download_icon_as_image(
                icon_id=5518010,
                color="4169E1",
                size=400,
                ctx=ctx
            )
            print(f"Downloaded image content type: {type(image_content)}")
        except Exception as e:
            print(f"Error in download_icon_as_image: {str(e)}")
            traceback.print_exc()
        
        # Test the search_and_download_icons function
        print("\nTesting search_and_download_icons...")
        try:
            saved_files = await search_and_download_icons(
                query="fitness coach",
                output_directory=str(test_dir),
                limit=2,
                color="4169E1",
                size=400,
                ctx=ctx
            )
            print(f"Downloaded {len(saved_files)} files: {saved_files}")
        except Exception as e:
            print(f"Error in search_and_download_icons: {str(e)}")
            traceback.print_exc()
        
        print("\nMCP server tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"MCP server test failed: {str(e)}")
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    try:
        # Test the client
        await test_client()
        
        # Test the MCP server
        await test_mcp_server()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())