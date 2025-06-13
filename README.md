# Noun Project MCP Server

A Model Context Protocol (MCP) server for interfacing with The Noun Project API.

> **Note:** This code was AI generated and has not yet been deployed to PyPI.

## Installation

```bash
uv add mcp-noun-project
```

## Environment Variables

This MCP server requires the following environment variables:

- `NOUN_PROJECT_API_KEY` - Your Noun Project API key
- `NOUN_PROJECT_API_SECRET` - Your Noun Project API secret

You can either set these environment variables in your shell or create a `.env` file:

```
NOUN_PROJECT_API_KEY=your_api_key
NOUN_PROJECT_API_SECRET=your_api_secret
```

## Usage with Claude

Install this MCP server in Claude Desktop:

```bash
mcp install src/mcp_noun_project/server.py
```

This will configure the MCP server in your Claude Desktop application and allow it to be used in conversations.

## How Agents Should Use This MCP Server

### Available Tools

This MCP server provides the following tools for searching and retrieving icons:

- **search_icons** - Search for icons by term/keyword
- **get_icon_details** - Get detailed information about a specific icon
- **download_icon** - Download an icon in various formats (SVG, PNG)

### Best Practices for Agents

1. **Search First** - Always start with `search_icons` to find relevant icons before attempting to get details or download
2. **Be Specific** - Use descriptive search terms that match what the user is looking for (e.g., "email" instead of "communication")
3. **Check Results** - Review search results and select the most appropriate icon ID before proceeding
4. **Format Selection** - When downloading, consider the user's needs:
   - Use SVG for scalable graphics and web use
   - Use PNG for specific size requirements or when SVG isn't supported
5. **Attribution** - Always mention that icons are from The Noun Project and may require attribution depending on the license

### Example Usage Flow

```
1. User: "I need a search icon for my website"
2. Agent: Uses search_icons with term "search"
3. Agent: Reviews results and selects appropriate icon
4. Agent: Uses get_icon_details to get license information
5. Agent: Uses download_icon to get SVG format
6. Agent: Provides icon to user with attribution info
```

### Error Handling

- If search returns no results, try alternative search terms
- If download fails, check if the icon ID is valid
- Always handle API rate limits gracefully

## Development

For local development:

```bash
# Install dependencies
uv add -e .

# Run in development mode with the MCP Inspector
mcp dev src/mcp_noun_project/server.py
```