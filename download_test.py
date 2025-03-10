#!/usr/bin/env python3
"""Test downloading icons to a directory."""

import asyncio
import os
import traceback
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_noun_project.client import NounProjectClient


async def test_download(client, icon_id, color=None, size=200):
    """Test the download_icon method directly."""
    print(f"\nTesting download_icon for icon_id={icon_id}, color={color}, size={size}")
    try:
        icon_result = await client.download_icon(
            icon_id=icon_id, 
            color=color, 
            size=size
        )
        print(f"Download icon result keys: {list(icon_result.keys())}")
        
        if "icon" in icon_result:
            icon = icon_result["icon"]
            print(f"Icon name: {icon.get('name')}")
            print(f"Icon URL keys: {[k for k in icon.keys() if 'url' in k]}")
            for k in icon.keys():
                if 'url' in k:
                    print(f"  {k}: {icon.get(k)}")
        return True
    except Exception as e:
        print(f"Error in download_icon: {str(e)}")
        traceback.print_exc()
        return False


async def test_url(client, icon_id, color=None, size=200):
    """Test the get_icon_download_url method."""
    print(f"\nTesting get_icon_download_url for icon_id={icon_id}, color={color}, size={size}")
    try:
        url = await client.get_icon_download_url(
            icon_id=icon_id, 
            color=color, 
            size=size
        )
        print(f"Download URL: {url}")
        return url
    except Exception as e:
        print(f"Error in get_icon_download_url: {str(e)}")
        traceback.print_exc()
        return None


async def download_icon(client, icon_id, output_dir, color=None, size=200):
    """Download an icon to the specified directory."""
    print(f"\nDownloading icon {icon_id} to {output_dir}")
    try:
        # Get the download URL
        url = await test_url(client, icon_id, color, size)
        if not url:
            print(f"Failed to get URL for icon {icon_id}")
            return None
        
        # Get icon details for the filename
        result = await client.get_icon_by_id(icon_id, thumbnail_size=size)
        icon = result.get("icon", {})
        icon_name = icon.get("name", f"icon_{icon_id}")
        
        # Create a safe filename
        import re
        safe_name = re.sub(r'[^\w\-_.]', '_', icon_name)
        file_path = output_dir / f"{safe_name}_{icon_id}.png"
        
        # Download the image
        import httpx
        async with httpx.AsyncClient() as http_client:
            print(f"Downloading from URL: {url}")
            response = await http_client.get(url)
            response.raise_for_status()
            image_data = response.content
            
            # Save the image
            with open(file_path, "wb") as f:
                f.write(image_data)
        
        print(f"Successfully downloaded icon to {file_path}")
        return file_path
    
    except Exception as e:
        print(f"Error downloading icon {icon_id}: {str(e)}")
        traceback.print_exc()
        return None


async def main():
    """Run tests on the fixed client code."""
    print("=== Testing Noun Project API Client with Fixes ===")
    
    try:
        client = NounProjectClient()
        
        # Create test_icons directory if it doesn't exist
        output_dir = Path(__file__).parent / "test_icons"
        os.makedirs(output_dir, exist_ok=True)
        
        # Test with a specific icon ID that was failing
        test_icon_id = 5518010  # The one from your error message
        
        # Test the download_icon method
        await test_download(client, test_icon_id)
        
        # Test the get_icon_download_url method
        await test_url(client, test_icon_id)
        
        # Test downloading with the blue color (4169E1)
        await download_icon(client, test_icon_id, output_dir, color="4169E1", size=400)
        
        # Test searching and downloading
        print("\nTesting search functionality...")
        search_result = await client.search_icons(query="fitness coach", limit=2)
        icons = search_result.get("icons", [])
        
        if not icons:
            print("No icons found for 'fitness coach'")
        else:
            print(f"Found {len(icons)} icons for 'fitness coach'")
            for icon in icons:
                icon_id = icon.get("id")
                if icon_id:
                    await download_icon(client, icon_id, output_dir, color="4169E1", size=400)
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())