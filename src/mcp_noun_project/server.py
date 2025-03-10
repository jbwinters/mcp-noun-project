"""Noun Project MCP Server."""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP, Image
from mcp.types import ImageContent, TextContent

try:
    from mcp_noun_project.client import NounProjectClient
except ImportError:
    # For direct execution during development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.mcp_noun_project.client import NounProjectClient

# Load environment variables from .env file
load_dotenv()


@dataclass
class ServerContext:
    """Server context for the Noun Project API client."""

    client: NounProjectClient


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[ServerContext]:
    """Initialize the Noun Project API client."""
    try:
        # Initialize the Noun Project API client
        client = NounProjectClient()
        yield ServerContext(client=client)
    except Exception as e:
        print(f"Error initializing Noun Project API client: {e}", file=sys.stderr)
        sys.exit(1)


# Create the MCP server
mcp = FastMCP(
    "Noun Project",
    description="Search and retrieve icons from The Noun Project",
    lifespan=lifespan,
    dependencies=["httpx", "python-dotenv"],
)


@mcp.tool()
async def search_icons(
    query: str,
    limit: int = 10,
    public_domain_only: bool = False,
    thumbnail_size: Optional[int] = 84,
    include_svg: bool = False,
    ctx: Context = None,
) -> List[Dict[str, Any]]:
    """
    Search for icons by query term.

    Args:
        query: The search term to look for icons.
        limit: Maximum number of results to return (default: 10).
        public_domain_only: Limit results to public domain icons only (default: False).
        thumbnail_size: Size of thumbnails to return (42, 84, or 200) (default: 84).
        include_svg: Include SVG data in the response (default: False).
        ctx: MCP context.

    Returns:
        A list of icon objects.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.search_icons(
        query=query,
        limit=limit,
        public_domain_only=public_domain_only,
        thumbnail_size=thumbnail_size,
        include_svg=include_svg,
    )
    
    return result.get("icons", [])


@mcp.tool()
async def get_icon_by_id(
    icon_id: Union[str, int],
    thumbnail_size: Optional[int] = 84,
    ctx: Context = None,
) -> Dict[str, Any]:
    """
    Get an icon by its ID.

    Args:
        icon_id: The ID of the icon to retrieve.
        thumbnail_size: Size of thumbnail to return (42, 84, or 200) (default: 84).
        ctx: MCP context.

    Returns:
        The icon object.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.get_icon_by_id(
        icon_id=icon_id,
        thumbnail_size=thumbnail_size,
    )
    
    return result.get("icon", {})


@mcp.tool()
async def download_icon_as_image(
    icon_id: Union[str, int],
    color: Optional[str] = None,
    size: int = 200,
    ctx: Context = None,
) -> ImageContent:
    """
    Download an icon and return it as an image.

    Args:
        icon_id: The ID of the icon to download.
        color: Hexadecimal color value (e.g., "FF0000" for red).
        size: Size of the image in pixels (default: 200).
        ctx: MCP context.

    Returns:
        The icon as an image.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.download_icon(
        icon_id=icon_id,
        color=color,
        filetype="png",
        size=size,
    )
    
    # Get the icon data
    icon_data = result.get("icon", {})
    
    # Get the preview URL from the icon data
    icon_url = icon_data.get("preview_url") or icon_data.get("thumbnail_url")
    
    if not icon_url:
        raise ValueError("No preview URL found in the API response")
    
    # Download the image
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(icon_url)
        response.raise_for_status()
        image_data = response.content
    
    # Return the image as an MCP Image
    return ImageContent(
        type="image",
        data=image_data,
        format="png",
    )


@mcp.tool()
async def search_collections(
    query: str,
    limit: int = 10,
    ctx: Context = None,
) -> List[Dict[str, Any]]:
    """
    Search for collections by query term.

    Args:
        query: The search term to look for collections.
        limit: Maximum number of results to return (default: 10).
        ctx: MCP context.

    Returns:
        A list of collection objects.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.get_collections(
        query=query,
        limit=limit,
    )
    
    return result.get("collections", [])


@mcp.tool()
async def get_collection_by_id(
    collection_id: Union[str, int],
    limit: int = 10,
    thumbnail_size: Optional[int] = 84,
    include_svg: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    """
    Get a collection by its ID.

    Args:
        collection_id: The ID of the collection to retrieve.
        limit: Maximum number of icon results (default: 10).
        thumbnail_size: Size of thumbnails to return (42, 84, or 200) (default: 84).
        include_svg: Include SVG data in the response (default: False).
        ctx: MCP context.

    Returns:
        The collection object with its icons.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.get_collection_by_id(
        collection_id=collection_id,
        limit=limit,
        thumbnail_size=thumbnail_size,
        include_svg=include_svg,
    )
    
    return result.get("collection", {})


@mcp.tool()
async def autocomplete_search(
    query: str,
    limit: int = 10,
    ctx: Context = None,
) -> List[str]:
    """
    Get autocomplete suggestions for a query.

    Args:
        query: The partial search term to get suggestions for.
        limit: Maximum number of results to return (default: 10).
        ctx: MCP context.

    Returns:
        A list of suggested search terms.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.autocomplete(
        query=query,
        limit=limit,
    )
    
    suggestions = []
    for suggestion in result.get("suggestions", []):
        term = suggestion.get("term")
        if term:
            suggestions.append(term)
    
    return suggestions


@mcp.tool()
async def download_icon_to_file(
    icon_id: Union[str, int],
    output_path: str,
    color: Optional[str] = None,
    size: int = 200,
    ctx: Context = None,
) -> str:
    """
    Download an icon and save it to a file.

    Args:
        icon_id: The ID of the icon to download.
        output_path: Path where the icon should be saved. Can be a directory or a file path.
        color: Hexadecimal color value (e.g., "FF0000" for red).
        size: Size of the image in pixels (default: 200).
        ctx: MCP context.

    Returns:
        The path to the saved file.
    """
    import os
    import httpx
    from pathlib import Path
    
    client = ctx.request_context.lifespan_context.client
    result = await client.download_icon(
        icon_id=icon_id,
        color=color,
        filetype="png",
        size=size,
    )
    
    # Get the icon URL and name from the response
    icon_data = result.get("icon", {})
    icon_url = icon_data.get("preview_url")
    icon_name = icon_data.get("name", f"icon_{icon_id}")
    
    if not icon_url:
        raise ValueError("No preview URL found in the API response")
    
    # Sanitize the icon name for use in a filename
    import re
    safe_name = re.sub(r'[^\w\-_.]', '_', icon_name)
    
    # Determine the output file path
    output_path = Path(output_path)
    
    if output_path.is_dir():
        # If output_path is a directory, create a filename using the icon name
        file_path = output_path / f"{safe_name}_{icon_id}.png"
    else:
        # If output_path is not a directory, use it directly (creating parent dirs if needed)
        os.makedirs(output_path.parent, exist_ok=True)
        file_path = output_path
    
    # Download the image
    async with httpx.AsyncClient() as client:
        response = await client.get(icon_url)
        response.raise_for_status()
        image_data = response.content
    
    # Save the image to the file
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    return str(file_path)


@mcp.tool()
async def search_and_download_icons(
    query: str,
    output_directory: str,
    limit: int = 5,
    public_domain_only: bool = False,
    color: Optional[str] = None,
    size: int = 200,
    ctx: Context = None,
) -> List[str]:
    """
    Search for icons and download them to a directory.

    Args:
        query: The search term to look for icons.
        output_directory: Directory where icons should be saved.
        limit: Maximum number of icons to download (default: 5).
        public_domain_only: Limit results to public domain icons only (default: False).
        color: Hexadecimal color value (e.g., "FF0000" for red).
        size: Size of the images in pixels (default: 200).
        ctx: MCP context.

    Returns:
        A list of paths to the saved icon files.
    """
    import os
    import httpx
    import asyncio
    from pathlib import Path
    import re
    
    # Ensure the output directory exists
    output_dir = Path(output_directory)
    os.makedirs(output_dir, exist_ok=True)
    
    # Search for icons
    client = ctx.request_context.lifespan_context.client
    search_result = await client.search_icons(
        query=query,
        limit=limit,
        public_domain_only=public_domain_only,
    )
    
    icons = search_result.get("icons", [])
    if not icons:
        return []
    
    saved_files = []
    
    # Process each icon
    for icon in icons:
        try:
            icon_id = icon.get("id")
            icon_name = icon.get("name", f"icon_{icon_id}")
            
            # Sanitize the icon name for use in a filename
            safe_name = re.sub(r'[^\w\-_.]', '_', icon_name)
            file_path = output_dir / f"{safe_name}_{icon_id}.png"
            
            # Download the icon
            download_result = await client.download_icon(
                icon_id=icon_id,
                color=color,
                filetype="png",
                size=size,
            )
            
            # Get the icon data
            icon_data = download_result.get("icon", {})
            
            # Get the preview URL from the icon data
            icon_url = icon_data.get("preview_url") or icon_data.get("thumbnail_url")
            
            if not icon_url:
                ctx.warning(f"No preview URL found for icon {icon_id}, skipping")
                continue
            
            # Download the image
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(icon_url)
                response.raise_for_status()
                image_data = response.content
            
            # Save the image to a file
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            saved_files.append(str(file_path))
            ctx.info(f"Downloaded icon {icon_id} to {file_path}")
            
            # Add a small delay between downloads to avoid rate limiting
            await asyncio.sleep(0.2)
            
        except Exception as e:
            ctx.error(f"Error downloading icon {icon.get('id')}: {str(e)}")
    
    return saved_files


@mcp.tool()
async def get_api_usage(
    ctx: Context = None,
) -> Dict[str, Any]:
    """
    Get API usage information.

    Args:
        ctx: MCP context.

    Returns:
        API usage information including limits and current usage.
    """
    client = ctx.request_context.lifespan_context.client
    result = await client.get_usage()
    
    return result.get("usage", {})


@mcp.resource("documentation://usage")
async def get_usage_documentation() -> str:
    """Get documentation on API usage and rate limits."""
    return """
    # The Noun Project API Usage

    The Noun Project API has rate limits based on your subscription level.
    Each API call counts towards your daily and monthly limits.

    ## Rate Limits

    - Free tier: 5,000 API calls per month
    - Plus tier: 100,000 API calls per month
    - Premium tier: 500,000 API calls per month
    
    ## Best Practices

    1. Use the autocomplete_search tool to refine searches before using search_icons
    2. Request only the data you need (limit results to save API calls)
    3. Use thumbnail_size parameter to get appropriately sized images
    4. Specify public_domain_only=True if you need royalty-free icons
    """


@mcp.resource("documentation://getting-started")
async def get_getting_started_documentation() -> str:
    """Get documentation on how to use the Noun Project MCP server."""
    return """
    # Getting Started with The Noun Project API

    The Noun Project provides access to over 3 million icons created by designers worldwide.
    This MCP server allows you to search and retrieve icons from The Noun Project collection.

    ## Available Tools

    - search_icons: Search for icons by keyword
    - get_icon_by_id: Get details for a specific icon
    - download_icon_as_image: Download an icon as an image
    - download_icon_to_file: Download an icon and save it to a file
    - search_and_download_icons: Search for icons and download them all to a directory
    - search_collections: Search for collections of icons
    - get_collection_by_id: Get details for a specific collection
    - autocomplete_search: Get search term suggestions
    - get_api_usage: Check your API usage and limits

    ## Example Usage

    1. Search for icons related to a topic:
       ```
       search_icons(query="cat", limit=5)
       ```

    2. Get autocomplete suggestions:
       ```
       autocomplete_search(query="prog")  # Returns terms like "programming", "progress", etc.
       ```

    3. Download an icon as an image:
       ```
       download_icon_as_image(icon_id=1234, color="FF0000", size=200)
       ```

    4. Download an icon to a file:
       ```
       download_icon_to_file(icon_id=1234, output_path="/path/to/save/folder", color="FF0000")
       ```
       
    5. Search for icons and download them all at once:
       ```
       search_and_download_icons(query="dog", output_directory="/path/to/icons", limit=10, color="FF0000")
       ```
    """


if __name__ == "__main__":
    """Run the MCP server directly."""
    mcp.run()