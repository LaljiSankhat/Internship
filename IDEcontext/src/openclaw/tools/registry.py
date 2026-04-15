"""Tool registry — discover, register, and invoke tools."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Coroutine

from openclaw.models import ToolParameter, ToolResult

logger = logging.getLogger("openclaw.tools")

# Type alias for an async tool function
ToolFunc = Callable[..., Coroutine[Any, Any, ToolResult]]


class _ToolEntry:
    """Internal wrapper around a registered tool."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, ToolParameter],
        func: ToolFunc,
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_openai_schema(self) -> dict[str, Any]:
        """Return the tool definition in OpenAI function-calling format."""
        props: dict[str, Any] = {}
        required: list[str] = []
        for pname, param in self.parameters.items():
            props[pname] = {"type": param.type, "description": param.description}
            if param.default is not None:
                props[pname]["default"] = param.default
            if param.required:
                required.append(pname)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    **({"required": required} if required else {}),
                },
            },
        }


class ToolRegistry:
    """Central catalogue of all available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, _ToolEntry] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, ToolParameter],
        func: ToolFunc,
    ) -> None:
        self._tools[name] = _ToolEntry(name, description, parameters, func)
        logger.debug("Registered tool: %s", name)

    def get(self, name: str) -> _ToolEntry | None:
        return self._tools.get(name)

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def openai_schemas(self) -> list[dict[str, Any]]:
        return [t.to_openai_schema() for t in self._tools.values()]

    async def invoke(self, name: str, arguments_json: str, **ctx: Any) -> ToolResult:
        entry = self._tools.get(name)
        if not entry:
            return ToolResult(success=False, output=f"Unknown tool: {name}")
        try:
            args = json.loads(arguments_json) if arguments_json else {}
            return await entry.func(**args, **ctx)
        except Exception as exc:
            logger.exception("Tool %s failed", name)
            return ToolResult(success=False, output=f"Error: {exc}")


# ── decorator for convenience ────────────────────────────────────────

# Module-level default registry (populated by built-in tools)
_default_registry = ToolRegistry()


def tool(
    name: str,
    description: str,
    parameters: dict[str, ToolParameter] | None = None,
) -> Callable[[ToolFunc], ToolFunc]:
    """Decorator that registers a function in the default registry."""

    def decorator(func: ToolFunc) -> ToolFunc:
        _default_registry.register(name, description, parameters or {}, func)
        return func

    return decorator


def get_default_registry() -> ToolRegistry:
    return _default_registry
