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

## Development

For local development:

```bash
# Install dependencies
uv add -e .

# Run in development mode with the MCP Inspector
mcp dev src/mcp_noun_project/server.py
```