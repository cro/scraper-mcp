# Scraper MCP

[![CI](https://github.com/cotdp/scraper-mcp/workflows/CI/badge.svg)](https://github.com/cotdp/scraper-mcp/actions/workflows/ci.yml)
[![Docker](https://github.com/cotdp/scraper-mcp/workflows/Build%20and%20Push%20Docker%20Images/badge.svg)](https://github.com/cotdp/scraper-mcp/actions/workflows/docker-publish.yml)
[![Docker Hub](https://img.shields.io/docker/v/cotdp/scraper-mcp?label=Docker%20Hub)](https://hub.docker.com/r/cotdp/scraper-mcp)

A context-optimized MCP server for web scraping. Reduces LLM token usage by 70-90% through server-side HTML filtering, markdown conversion, and CSS selector targeting.

## Quick Start

```bash
# Run with Docker
docker run -d -p 8000:8000 --name scraper-mcp cotdp/scraper-mcp:latest

# Add to Claude Code
claude mcp add --transport http scraper http://localhost:8000/mcp --scope user
```

Try it:
```
> scrape https://example.com
> scrape and filter .article-content from https://blog.example.com/post
```

**Endpoints:**
- MCP: `http://localhost:8000/mcp`
- Dashboard: `http://localhost:8000/`

## Features

### Web Scraping
- **4 scraping modes**: Raw HTML, markdown, plain text, link extraction
- **CSS selector filtering**: Extract only relevant content server-side
- **Batch operations**: Process multiple URLs concurrently
- **Smart caching**: Three-tier cache system (realtime/default/static)
- **Retry logic**: Exponential backoff for transient failures

### Perplexity AI Integration
- **Web search**: AI-powered search with citations (`perplexity` tool)
- **Reasoning**: Complex analysis with step-by-step reasoning (`perplexity_reason` tool)
- Requires `PERPLEXITY_API_KEY` environment variable

### Monitoring Dashboard
- Real-time request statistics and cache metrics
- Interactive API playground for testing tools
- Runtime configuration without restarts

![Dashboard](docs/1-dashboard.png)

See [Dashboard Guide](docs/DASHBOARD.md) for details.

## Available Tools

| Tool | Description |
|------|-------------|
| `scrape_url` | HTML converted to markdown (best for LLMs) |
| `scrape_url_html` | Raw HTML content |
| `scrape_url_text` | Plain text extraction |
| `scrape_extract_links` | Extract all links with metadata |
| `perplexity` | AI web search with citations |
| `perplexity_reason` | Complex reasoning tasks |

All tools support:
- Single URL or batch operations (pass array)
- `timeout` and `max_retries` parameters
- `css_selector` for targeted extraction

## Resources

MCP resources provide read-only data access via URI-based addressing:

| URI | Description |
|-----|-------------|
| `cache://stats` | Cache hit rate, size, entry counts |
| `cache://requests` | List of recent request IDs |
| `cache://request/{id}` | Retrieve cached result by ID |
| `config://current` | Current runtime configuration |
| `config://scraping` | Timeout, retries, concurrency |
| `server://info` | Version, uptime, capabilities |
| `server://metrics` | Request counts, success rates |

## Prompts

MCP prompts provide reusable workflow templates:

| Prompt | Description |
|--------|-------------|
| `analyze_webpage` | Structured webpage analysis |
| `summarize_content` | Generate content summaries |
| `extract_data` | Extract specific data types |
| `seo_audit` | Comprehensive SEO check |
| `link_audit` | Analyze internal/external links |
| `research_topic` | Multi-source research |
| `fact_check` | Verify claims across sources |

See [API Reference](docs/API.md) for complete documentation.

## Docker Compose

For persistent storage and custom configuration:

```yaml
# docker-compose.yml
services:
  scraper-mcp:
    image: cotdp/scraper-mcp:latest
    ports:
      - "8000:8000"
    volumes:
      - cache:/app/cache
    restart: unless-stopped

volumes:
  cache:
```

```bash
docker-compose up -d
```

## Configuration

Create a `.env` file for custom settings:

```bash
# Perplexity AI (optional)
PERPLEXITY_API_KEY=your_key_here

# Proxy (optional)
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080

# ScrapeOps proxy service (optional)
SCRAPEOPS_API_KEY=your_key_here
SCRAPEOPS_RENDER_JS=true
```

See [Configuration Guide](docs/CONFIGURATION.md) for all options.

## Claude Desktop

Add to your MCP settings:

```json
{
  "mcpServers": {
    "scraper": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Claude Code Skills

This project includes [Agent Skills](https://docs.anthropic.com/en/docs/claude-code/skills) that provide Claude Code with specialized knowledge for using the scraper tools effectively.

| Skill | Description |
|-------|-------------|
| [web-scraping](.claude/skills/web-scraping/SKILL.md) | CSS selectors, batch operations, retry configuration |
| [perplexity](.claude/skills/perplexity/SKILL.md) | AI search, reasoning tasks, conversation patterns |

### Install Skills

Copy the skills to your Claude Code skills directory:

```bash
# Clone or download this repo, then:
cp -r .claude/skills/web-scraping ~/.claude/skills/
cp -r .claude/skills/perplexity ~/.claude/skills/
```

Or install directly:

```bash
# web-scraping skill
mkdir -p ~/.claude/skills/web-scraping
curl -o ~/.claude/skills/web-scraping/SKILL.md \
  https://raw.githubusercontent.com/cotdp/scraper-mcp/main/.claude/skills/web-scraping/SKILL.md

# perplexity skill
mkdir -p ~/.claude/skills/perplexity
curl -o ~/.claude/skills/perplexity/SKILL.md \
  https://raw.githubusercontent.com/cotdp/scraper-mcp/main/.claude/skills/perplexity/SKILL.md
```

Once installed, Claude Code will automatically use these skills when performing web scraping or Perplexity AI tasks.

## Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | Complete tool documentation, parameters, CSS selectors |
| [Configuration](docs/CONFIGURATION.md) | Environment variables, proxy setup, ScrapeOps |
| [Dashboard](docs/DASHBOARD.md) | Monitoring UI, playground, runtime config |
| [Development](docs/DEVELOPMENT.md) | Local setup, architecture, contributing |
| [Testing](docs/TESTING.md) | Test suite, coverage, adding tests |

## Local Development

```bash
# Install
uv pip install -e ".[dev]"

# Run
python -m scraper_mcp

# Test
pytest

# Lint
ruff check . && mypy src/
```

See [Development Guide](docs/DEVELOPMENT.md) for details.

## License

MIT License

---

_Last updated: December 18, 2025_
