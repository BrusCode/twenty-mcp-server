"""
Tests for Twenty MCP Server
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from twenty_mcp_server.config import Config, Workspace
from twenty_mcp_server.client import TwentyClient, TwentyClientManager, TwentyAPIError


@pytest.fixture
def mock_workspace():
    return Workspace(name="test", base_url="https://test.com", api_key="test_key")


@pytest.fixture
def mock_config(mock_workspace):
    config = MagicMock()
    config.workspaces = {"test": mock_workspace}
    config.default_workspace = "test"
    config.timeout = 30
    config.rate_limit = 100
    config.get_workspace = MagicMock(return_value=mock_workspace)
    config.get_all_workspaces = MagicMock(return_value=["test"])
    return config


class TestWorkspace:
    def test_workspace_creation(self):
        ws = Workspace(name="test", base_url="https://test.com", api_key="key")
        assert ws.name == "test"
        assert ws.base_url == "https://test.com"
        assert ws.api_key == "key"
        assert ws.is_valid is True

    def test_workspace_invalid(self):
        ws = Workspace(name="", base_url="", api_key="")
        assert ws.is_valid is False


class TestTwentyClient:
    @pytest.mark.asyncio
    async def test_get_headers(self, mock_workspace):
        client = TwentyClient(mock_workspace)
        headers = client.get_headers()
        assert headers["Authorization"] == "Bearer test_key"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_record_success(self, mock_workspace):
        client = TwentyClient(mock_workspace)

        mock_response = {
            "data": {
                "findPerson": {
                    "id": "123",
                    "firstName": "John",
                    "lastName": "Doe",
                }
            }
        }

        with patch.object(client, "make_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_response
            result = await client.get_record("people", "123")
            assert result == mock_response
            mock_req.assert_called_once_with("GET", "/rest/people/123")


@pytest.mark.skip(reason="Integration test - requires real API credentials")
@pytest.mark.asyncio
async def test_integration():
    """Integration test - requires real API credentials"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("TWENTY_API_KEY")
    base_url = os.getenv("TWENTY_BASE_URL")

    if not api_key or not base_url:
        pytest.skip("No API credentials provided")

    workspace = Workspace(name="integration", base_url=base_url, api_key=api_key)
    client = TwentyClient(workspace)

    try:
        result = await client.get_objects()
        assert "data" in result
        print("✓ Integration test passed: Successfully connected to API")
    except Exception as e:
        pytest.fail(f"Integration test failed: {e}")
