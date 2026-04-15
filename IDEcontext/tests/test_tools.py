"""Basic tests for the OpenClaw tool registry."""

import asyncio
import pytest

from openclaw.tools.registry import ToolRegistry, get_default_registry
from openclaw.models import ToolParameter, ToolResult


@pytest.fixture
def registry() -> ToolRegistry:
    return ToolRegistry()


@pytest.mark.asyncio
async def test_register_and_invoke(registry: ToolRegistry) -> None:
    async def echo(text: str = "hello", **_: object) -> ToolResult:
        return ToolResult(success=True, output=f"echo: {text}")

    registry.register(
        name="echo",
        description="Echo a string",
        parameters={"text": ToolParameter(type="string", description="Text to echo")},
        func=echo,
    )

    assert "echo" in registry.list_names()
    result = await registry.invoke("echo", '{"text": "world"}')
    assert result.success
    assert result.output == "echo: world"


@pytest.mark.asyncio
async def test_unknown_tool(registry: ToolRegistry) -> None:
    result = await registry.invoke("nonexistent", "{}")
    assert not result.success
    assert "Unknown tool" in result.output


def test_default_registry_has_builtins() -> None:
    import openclaw.tools.builtins  # noqa: F401

    reg = get_default_registry()
    names = reg.list_names()
    assert "exec" in names
    assert "read_file" in names
    assert "write_file" in names
    assert "list_dir" in names
    assert "web_search" in names


def test_openai_schema() -> None:
    import openclaw.tools.builtins  # noqa: F401

    reg = get_default_registry()
    schemas = reg.openai_schemas()
    assert len(schemas) > 0
    for s in schemas:
        assert s["type"] == "function"
        assert "name" in s["function"]
        assert "parameters" in s["function"]
