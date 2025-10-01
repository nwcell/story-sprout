from pydantic_ai.messages import ModelMessage, ToolReturnPart

MESSAGE_WINDOW = 15


async def message_at_index_contains_tool_return_parts(messages: list[ModelMessage], index: int) -> bool:
    return any(isinstance(part, ToolReturnPart) for part in messages[index].parts)


# TODO: Make sure we're not nuking system messages
async def keep_recent_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    message_window = MESSAGE_WINDOW
    if len(messages) <= message_window:
        return messages
    if await message_at_index_contains_tool_return_parts(messages, len(messages) - message_window):
        return messages
    return messages[-message_window:]
