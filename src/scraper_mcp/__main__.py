"""Main entry point for the scraper MCP server."""

from __future__ import annotations

import argparse

from scraper_mcp.server import run_server


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scraper MCP Server - Context-optimized web scraping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scraper_mcp                           # Default: streamable-http on 0.0.0.0:8000
  python -m scraper_mcp sse                       # Use SSE transport
  python -m scraper_mcp streamable-http 0.0.0.0 9000  # Custom port
  python -m scraper_mcp --disable-prompts         # Disable MCP prompts
        """,
    )

    parser.add_argument(
        "transport",
        nargs="?",
        default="streamable-http",
        choices=["streamable-http", "sse"],
        help="Transport type (default: streamable-http)",
    )
    parser.add_argument(
        "host",
        nargs="?",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--disable-resources",
        action="store_true",
        help="Disable MCP resources (reduces context overhead)",
    )
    parser.add_argument(
        "--disable-prompts",
        action="store_true",
        help="Disable MCP prompts (reduces context overhead)",
    )

    args = parser.parse_args()

    print(f"Starting Scraper MCP server on {args.host}:{args.port} ({args.transport})...")

    if args.disable_resources:
        print("  - Resources: DISABLED")
    if args.disable_prompts:
        print("  - Prompts: DISABLED")

    run_server(
        transport=args.transport,
        host=args.host,
        port=args.port,
        enable_resources=not args.disable_resources,
        enable_prompts=not args.disable_prompts,
    )


if __name__ == "__main__":
    main()
