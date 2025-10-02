import logging
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.toolsets import ToolsetTool, WrapperToolset

logger = logging.getLogger(__name__)


class EnhancedToolset(WrapperToolset):
    """Generic toolset wrapper for preventing duplicate executions and future enhancements."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_call: tuple[str, dict[str, Any]] | None = None

    async def call_tool(self, name: str, tool_args: dict[str, Any], ctx: RunContext, tool: ToolsetTool) -> Any:
        logger.info(f"toolset.call_tool({name}, {tool_args})")
        call_signature = (name, tool_args)

        # Block consecutive duplicate calls
        if self._last_call == call_signature:
            logger.warning(f"Blocked duplicate tool call: {name}")
            return {
                "status": "already_completed",
                "message": (
                    f"Task already completed - '{name}' was just executed successfully "
                    f"with these exact parameters. No need to repeat this action."
                ),
            }

        self._last_call = call_signature
        return await super().call_tool(name, tool_args, ctx, tool)
