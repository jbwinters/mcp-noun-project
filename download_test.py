#!/usr/bin/env python3
"""Test downloading icons to a directory."""

import asyncio
import os
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_noun_project.client import NounProjectClient


async def download_icon(client, icon_id, output_dir):
    """Download an icon to the specified directory."""
    # Get icon details
    result = await client.get_icon_by_id(icon_id, thumbnail_size=200)
    icon = result.get("icon", {})
    icon_name = icon.get("name", f"icon_{icon_id}")
    
    # Get the download URL
    preview_url = icon.get("preview_url") or icon.get("thumbnail_url")
    if not preview_url:
        print(f"No preview URL found for icon {icon_id}")
        return None
    
    # Create a safe filename
    import re
    safe_name = re.sub(r'[^\w\-_.]', '_', icon_name)
    file_path = output_dir / f"{safe_name}_{icon_id}.png"
    
    # Download the image
    import httpx
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(preview_url)
        response.raise_for_status()
        image_data = response.content
        
        # Save the image
        with open(file_path, "wb") as f:
            f.write(image_data)
    
    print(f"Downloaded icon to {file_path}")
    return file_path


async def main():
    """Download a test icon."""
    client = NounProjectClient()
    
    # Create test_icons directory if it doesn't exist
    output_dir = Path(__file__).parent / "test_icons"
    os.makedirs(output_dir, exist_ok=True)
    
    # Search for icons
    print("Searching for icons...")
    search_result = await client.search_icons(query="computer", limit=3)
    icons = search_result.get("icons", [])
    
    if not icons:
        print("No icons found")
        return
    
    # Download each icon
    for icon in icons:
        icon_id = icon.get("id")
        await download_icon(client, icon_id, output_dir)


if __name__ == "__main__":
    asyncio.run(main())