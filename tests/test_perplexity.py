"""Tests for Perplexity AI integration."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from scraper_mcp.models.perplexity import PerplexityResponse


class TestPerplexityService:
    """Tests for PerplexityService."""

    def test_is_available_without_api_key(self) -> None:
        """Test is_available returns False when API key is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove PERPLEXITY_API_KEY if it exists
            os.environ.pop("PERPLEXITY_API_KEY", None)

            from scraper_mcp.services.perplexity_service import PerplexityService

            assert PerplexityService.is_available() is False

    def test_is_available_with_api_key(self) -> None:
        """Test is_available returns True when API key is set and SDK is available."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            # Also need to patch PERPLEXITY_AVAILABLE
            with patch(
                "scraper_mcp.services.perplexity_service.PERPLEXITY_AVAILABLE", True
            ):
                from scraper_mcp.services.perplexity_service import PerplexityService

                assert PerplexityService.is_available() is True

    def test_is_available_without_sdk(self) -> None:
        """Test is_available returns False when SDK is not installed."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            with patch(
                "scraper_mcp.services.perplexity_service.PERPLEXITY_AVAILABLE", False
            ):
                from scraper_mcp.services.perplexity_service import PerplexityService

                assert PerplexityService.is_available() is False

    def test_default_configuration(self) -> None:
        """Test default configuration values."""
        with patch.dict(
            os.environ,
            {
                "PERPLEXITY_API_KEY": "test-key",
            },
            clear=True,
        ):
            # Clear any existing env vars we want to test defaults for
            os.environ.pop("PERPLEXITY_MODEL", None)
            os.environ.pop("PERPLEXITY_TEMPERATURE", None)
            os.environ.pop("PERPLEXITY_MAX_TOKENS", None)

            from scraper_mcp.services.perplexity_service import PerplexityService

            service = PerplexityService()

            assert service.default_model == "sonar"
            assert service.default_temperature == 0.3
            assert service.default_max_tokens == 4000
            assert service.reasoning_model == "sonar-reasoning-pro"

    def test_custom_configuration(self) -> None:
        """Test custom configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "PERPLEXITY_API_KEY": "test-key",
                "PERPLEXITY_MODEL": "sonar-pro",
                "PERPLEXITY_TEMPERATURE": "0.7",
                "PERPLEXITY_MAX_TOKENS": "8000",
            },
        ):
            from scraper_mcp.services.perplexity_service import PerplexityService

            service = PerplexityService()

            assert service.default_model == "sonar-pro"
            assert service.default_temperature == 0.7
            assert service.default_max_tokens == 8000


class TestPerplexityServiceChat:
    """Tests for PerplexityService.chat method."""

    @pytest.mark.asyncio
    async def test_chat_success(self) -> None:
        """Test successful chat completion."""
        # Create mock completion response
        mock_choice = Mock()
        mock_choice.message = Mock()
        mock_choice.message.content = "This is a test response about AI."

        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.citations = ["https://example.com/source1"]
        mock_completion.usage = mock_usage
        mock_completion.id = "req_test123"

        # Create mock client
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_completion)

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            with patch(
                "scraper_mcp.services.perplexity_service.PERPLEXITY_AVAILABLE", True
            ):
                with patch(
                    "scraper_mcp.services.perplexity_service.Perplexity",
                    return_value=mock_client,
                ):
                    from scraper_mcp.services.perplexity_service import PerplexityService

                    service = PerplexityService()
                    response = await service.chat(
                        messages=[{"role": "user", "content": "What is AI?"}],
                        model="sonar",
                    )

                    assert response.content == "This is a test response about AI."
                    assert response.model == "sonar"
                    assert "https://example.com/source1" in response.citations
                    assert response.usage["prompt_tokens"] == 10
                    assert response.usage["completion_tokens"] == 20
                    assert response.usage["total_tokens"] == 30
                    assert response.metadata["request_id"] == "req_test123"
                    assert "elapsed_ms" in response.metadata

    @pytest.mark.asyncio
    async def test_chat_without_client(self) -> None:
        """Test chat returns error when client is not available."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PERPLEXITY_API_KEY", None)

            with patch(
                "scraper_mcp.services.perplexity_service.PERPLEXITY_AVAILABLE", False
            ):
                from scraper_mcp.services.perplexity_service import PerplexityService

                service = PerplexityService()
                response = await service.chat(
                    messages=[{"role": "user", "content": "What is AI?"}]
                )

                assert response.content == ""
                assert "error" in response.metadata
                assert "not available" in response.metadata["error"]

    @pytest.mark.asyncio
    async def test_chat_rate_limit_error(self) -> None:
        """Test chat handles rate limit errors."""
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(
            side_effect=Exception("Rate limit exceeded")
        )

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            with patch(
                "scraper_mcp.services.perplexity_service.PERPLEXITY_AVAILABLE", True
            ):
                with patch(
                    "scraper_mcp.services.perplexity_service.Perplexity",
                    return_value=mock_client,
                ):
                    from scraper_mcp.services.perplexity_service import PerplexityService

                    service = PerplexityService()
                    response = await service.chat(
                        messages=[{"role": "user", "content": "What is AI?"}]
                    )

                    assert response.content == ""
                    assert "error" in response.metadata


class TestPerplexityServiceReason:
    """Tests for PerplexityService.reason method."""

    @pytest.mark.asyncio
    async def test_reason_uses_reasoning_model(self) -> None:
        """Test reason method uses the reasoning model."""
        mock_choice = Mock()
        mock_choice.message = Mock()
        mock_choice.message.content = "Reasoned response about the topic."

        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.citations = []
        mock_completion.usage = Mock(
            prompt_tokens=15, completion_tokens=25, total_tokens=40
        )
        mock_completion.id = "req_reason123"

        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_completion)

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            with patch(
                "scraper_mcp.services.perplexity_service.PERPLEXITY_AVAILABLE", True
            ):
                with patch(
                    "scraper_mcp.services.perplexity_service.Perplexity",
                    return_value=mock_client,
                ):
                    from scraper_mcp.services.perplexity_service import PerplexityService

                    service = PerplexityService()
                    response = await service.reason(
                        query="Compare solar vs wind energy"
                    )

                    # Verify the reasoning model was used
                    call_args = mock_client.chat.completions.create.call_args
                    assert call_args.kwargs["model"] == "sonar-reasoning-pro"

                    assert response.content == "Reasoned response about the topic."
                    assert response.model == "sonar-reasoning-pro"


class TestPerplexityTools:
    """Tests for Perplexity MCP tools."""

    @pytest.mark.asyncio
    async def test_perplexity_ask_tool(self) -> None:
        """Test perplexity_ask tool function."""
        mock_response = PerplexityResponse(
            content="Test response",
            model="sonar",
            citations=["https://example.com"],
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            metadata={"request_id": "test123"},
        )

        mock_service = Mock()
        mock_service.chat = AsyncMock(return_value=mock_response)

        with patch(
            "scraper_mcp.tools.router.get_perplexity_service",
            return_value=mock_service,
        ):
            from scraper_mcp.tools.router import perplexity_ask

            result = await perplexity_ask(
                messages=[{"role": "user", "content": "What is AI?"}],
                model="sonar-pro",
                temperature=0.5,
            )

            assert result.content == "Test response"
            assert result.model == "sonar"
            mock_service.chat.assert_called_once_with(
                messages=[{"role": "user", "content": "What is AI?"}],
                model="sonar-pro",
                temperature=0.5,
                max_tokens=None,
            )

    @pytest.mark.asyncio
    async def test_perplexity_reason_tool(self) -> None:
        """Test perplexity_reason tool function."""
        mock_response = PerplexityResponse(
            content="Reasoned analysis",
            model="sonar-reasoning-pro",
            citations=[],
            usage={"total_tokens": 50},
            metadata={},
        )

        mock_service = Mock()
        mock_service.reason = AsyncMock(return_value=mock_response)

        with patch(
            "scraper_mcp.tools.router.get_perplexity_service",
            return_value=mock_service,
        ):
            from scraper_mcp.tools.router import perplexity_reason

            result = await perplexity_reason(
                query="Analyze the impact of AI on jobs",
                temperature=0.3,
            )

            assert result.content == "Reasoned analysis"
            assert result.model == "sonar-reasoning-pro"
            mock_service.reason.assert_called_once_with(
                query="Analyze the impact of AI on jobs",
                temperature=0.3,
                max_tokens=None,
            )


class TestPerplexityResponse:
    """Tests for PerplexityResponse model."""

    def test_response_with_all_fields(self) -> None:
        """Test PerplexityResponse with all fields."""
        response = PerplexityResponse(
            content="Test content",
            model="sonar",
            citations=["https://example.com", "https://another.com"],
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            metadata={"request_id": "test123", "elapsed_ms": 150},
        )

        assert response.content == "Test content"
        assert response.model == "sonar"
        assert len(response.citations) == 2
        assert response.usage["total_tokens"] == 30
        assert response.metadata["elapsed_ms"] == 150

    def test_response_with_defaults(self) -> None:
        """Test PerplexityResponse with default values."""
        response = PerplexityResponse(
            content="Test content",
            model="sonar",
        )

        assert response.content == "Test content"
        assert response.model == "sonar"
        assert response.citations == []
        assert response.usage == {}
        assert response.metadata == {}

    def test_response_serialization(self) -> None:
        """Test PerplexityResponse can be serialized to dict."""
        response = PerplexityResponse(
            content="Test content",
            model="sonar",
            citations=["https://example.com"],
            usage={"total_tokens": 30},
            metadata={"request_id": "test123"},
        )

        data = response.model_dump()

        assert data["content"] == "Test content"
        assert data["model"] == "sonar"
        assert data["citations"] == ["https://example.com"]
        assert data["usage"]["total_tokens"] == 30
        assert data["metadata"]["request_id"] == "test123"
