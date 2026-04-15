"""Tests for the MCP server creation."""

import pytest
from openclaw.config import load_config
from openclaw.mcp_server import create_mcp_server


def test_mcp_server_creates() -> None:
    """Verify the MCP server can be instantiated without errors."""
    server = create_mcp_server()
    assert server is not None
