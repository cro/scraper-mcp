"""Pydantic models for Perplexity AI operations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PerplexityResponse(BaseModel):
    """Response model for Perplexity AI operations."""

    content: str = Field(description="Response content from Perplexity AI")
    model: str = Field(description="Model used for the response")
    citations: list[str] = Field(
        default_factory=list, description="Source URLs from web search"
    )
    usage: dict[str, int] = Field(
        default_factory=dict,
        description="Token usage: prompt_tokens, completion_tokens, total_tokens",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata (request_id, elapsed_ms, etc.)"
    )
