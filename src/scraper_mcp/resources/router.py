"""Resource registration for MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scraper_mcp.resources.cache import register_cache_resources
from scraper_mcp.resources.config import register_config_resources
from scraper_mcp.resources.server_info import register_server_resources

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def register_resources(mcp: FastMCP) -> None:
    """Register all MCP resources on the server.

    Resources provide read-only data access via URI-based addressing.
    They are analogous to GET endpoints in REST APIs.

    Args:
        mcp: The FastMCP server instance
    """
    # Cache resources: cache://stats, cache://requests, cache://request/{id}
    register_cache_resources(mcp)

    # Config resources: config://current, config://defaults, config://scraping, config://cache
    register_config_resources(mcp)

    # Server resources: server://info, server://metrics, server://tools
    register_server_resources(mcp)
