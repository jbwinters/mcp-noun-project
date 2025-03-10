#!/usr/bin/env python3
"""Test the Noun Project API client."""

import asyncio
import os
import sys
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


async def main():
    """Run all tests."""
    try:
        await test_client()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())