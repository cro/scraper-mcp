"""Cache resources for MCP server."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from scraper_mcp.cache import get_cache_stats
from scraper_mcp.cache_manager import get_cache_manager
from scraper_mcp.metrics import get_metrics

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def register_cache_resources(mcp: FastMCP) -> None:
    """Register cache-related resources on the MCP server.

    Args:
        mcp: The FastMCP server instance
    """

    @mcp.resource("cache://stats")
    def cache_stats_resource() -> str:
        """Current cache statistics including hit rate, size, and entry counts."""
        stats = get_cache_stats()
        return json.dumps(stats, indent=2)

    @mcp.resource("cache://requests")
    def cache_requests_resource() -> str:
        """List all recent request IDs with basic metadata.

        Returns request IDs from the metrics system that can be used
        to retrieve cached content.
        """
        metrics = get_metrics()
        requests = [
            {
                "request_id": r.request_id,
                "url": r.url,
                "timestamp": r.timestamp.isoformat(),
                "request_type": r.request_type,
                "success": r.success,
                "cache_key": r.cache_key,
            }
            for r in list(metrics.recent_requests)[::-1]  # Newest first
        ]
        return json.dumps(requests, indent=2)

    @mcp.resource("cache://request/{request_id}")
    def cache_request_resource(request_id: str) -> str:
        """Retrieve a cached scrape result by request ID.

        Args:
            request_id: The UUID of the request to retrieve
        """
        metrics = get_metrics()

        # Find the request in recent requests
        request = None
        for r in metrics.recent_requests:
            if r.request_id == request_id:
                request = r
                break

        if not request:
            return json.dumps({"error": "Request not found", "request_id": request_id})

        # Try to get cached content if cache_key exists
        cached_content = None
        if request.cache_key:
            cache_manager = get_cache_manager()
            cached_content = cache_manager.get(request.cache_key)

        result = {
            "request_id": request.request_id,
            "url": request.url,
            "timestamp": request.timestamp.isoformat(),
            "request_type": request.request_type,
            "success": request.success,
            "status_code": request.status_code,
            "elapsed_ms": request.elapsed_ms,
            "attempts": request.attempts,
            "error": request.error,
            "cached_content": cached_content,
            "perplexity_data": request.perplexity_data,
        }
        return json.dumps(result, indent=2, default=str)

    @mcp.resource("cache://request/{request_id}/content")
    def cache_request_content_resource(request_id: str) -> str:
        """Retrieve just the content from a cached request.

        Args:
            request_id: The UUID of the request to retrieve
        """
        metrics = get_metrics()

        # Find the request
        request = None
        for r in metrics.recent_requests:
            if r.request_id == request_id:
                request = r
                break

        if not request:
            return ""

        # Get cached content
        if request.cache_key:
            cache_manager = get_cache_manager()
            cached = cache_manager.get(request.cache_key)
            if cached and isinstance(cached, dict):
                content = cached.get("content", "")
                return str(content) if content else ""

        # For Perplexity requests, return the content
        if request.perplexity_data:
            content = request.perplexity_data.get("content", "")
            return str(content) if content else ""

        return ""

    @mcp.resource("cache://request/{request_id}/metadata")
    def cache_request_metadata_resource(request_id: str) -> str:
        """Retrieve just the metadata from a cached request.

        Args:
            request_id: The UUID of the request to retrieve
        """
        metrics = get_metrics()

        # Find the request
        request = None
        for r in metrics.recent_requests:
            if r.request_id == request_id:
                request = r
                break

        if not request:
            return json.dumps({"error": "Request not found"})

        metadata = {
            "request_id": request.request_id,
            "url": request.url,
            "timestamp": request.timestamp.isoformat(),
            "request_type": request.request_type,
            "success": request.success,
            "status_code": request.status_code,
            "elapsed_ms": request.elapsed_ms,
            "attempts": request.attempts,
        }

        # Add cached metadata if available
        if request.cache_key:
            cache_manager = get_cache_manager()
            cached = cache_manager.get(request.cache_key)
            if cached and isinstance(cached, dict):
                metadata["cached_metadata"] = cached.get("metadata", {})

        return json.dumps(metadata, indent=2, default=str)
