"""Noun Project API client."""

import os
import asyncio
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

# Load environment variables from .env file
load_dotenv()


class NounProjectClient:
    """Client for the Noun Project API."""

    def __init__(self) -> None:
        """Initialize the Noun Project API client."""
        self.api_key = os.environ.get("NOUN_PROJECT_API_KEY")
        self.api_secret = os.environ.get("NOUN_PROJECT_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "NOUN_PROJECT_API_KEY and NOUN_PROJECT_API_SECRET environment variables must be set"
            )
        
        self.base_url = "https://api.thenounproject.com"
        self.oauth = OAuth1Session(self.api_key, client_secret=self.api_secret)

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the Noun Project API using OAuth1."""
        url = f"{self.base_url}{path}"
        
        # Create a loop to run sync code in async context
        loop = asyncio.get_running_loop()
        
        # Prepare the request with parameters
        query_string = urlencode(params or {}) if params else ""
        full_url = f"{url}?{query_string}" if query_string else url
        
        # Run the OAuth request in a thread pool
        if method == "GET":
            response = await loop.run_in_executor(
                None, 
                lambda: self.oauth.get(full_url)
            )
        elif method == "POST":
            response = await loop.run_in_executor(
                None, 
                lambda: self.oauth.post(url, params=params, json=data)
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Check for errors
        response.raise_for_status()
        
        # Parse and return the JSON response
        return response.json()

    async def search_icons(
        self, 
        query: str, 
        limit: int = 10, 
        public_domain_only: bool = False,
        thumbnail_size: Optional[int] = None,
        include_svg: bool = False,
    ) -> Dict[str, Any]:
        """Search for icons by query term."""
        params = {
            "query": query,
            "limit": limit,
        }
        
        if public_domain_only:
            params["limit_to_public_domain"] = 1
            
        if thumbnail_size:
            params["thumbnail_size"] = thumbnail_size
            
        if include_svg:
            params["include_svg"] = 1
            
        return await self._request("GET", "/v2/icon", params)

    async def get_icon_by_id(
        self, 
        icon_id: Union[str, int],
        thumbnail_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get an icon by its ID."""
        params = {}
        if thumbnail_size:
            params["thumbnail_size"] = thumbnail_size
            
        return await self._request("GET", f"/v2/icon/{icon_id}", params)

    async def download_icon(
        self,
        icon_id: Union[str, int],
        color: Optional[str] = None,
        filetype: Optional[str] = None,
        size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get download information for an icon."""
        # For the download endpoint, we'll just use get_icon_by_id 
        # as the API doesn't provide a direct download API
        return await self.get_icon_by_id(icon_id, thumbnail_size=size or 200)
        
    async def get_icon_download_url(
        self,
        icon_id: Union[str, int],
        color: Optional[str] = None,
        size: Optional[int] = None,
    ) -> str:
        """Get the download URL for an icon."""
        result = await self.get_icon_by_id(icon_id, thumbnail_size=size or 200)
        icon = result.get("icon", {})
        
        # Get the preview URL from the icon data
        preview_url = icon.get("preview_url") or icon.get("thumbnail_url")
        if not preview_url:
            raise ValueError(f"No preview URL found for icon {icon_id}")
            
        return preview_url

    async def get_collections(
        self, 
        query: str, 
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Search for collections by query term."""
        params = {
            "query": query,
            "limit": limit,
        }
        
        return await self._request("GET", "/v2/collection", params)

    async def get_collection_by_id(
        self, 
        collection_id: Union[str, int],
        limit: int = 10,
        thumbnail_size: Optional[int] = None,
        include_svg: bool = False,
    ) -> Dict[str, Any]:
        """Get a collection by its ID."""
        params = {
            "limit": limit,
        }
        
        if thumbnail_size:
            params["thumbnail_size"] = thumbnail_size
            
        if include_svg:
            params["include_svg"] = 1
            
        return await self._request("GET", f"/v2/collection/{collection_id}", params)

    async def autocomplete(
        self, 
        query: str, 
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get autocomplete suggestions for a query."""
        params = {
            "query": query,
            "limit": limit,
        }
        
        return await self._request("GET", "/v2/icon/autocomplete", params)

    async def get_usage(self) -> Dict[str, Any]:
        """Get API usage information."""
        return await self._request("GET", "/v2/client/usage", {})