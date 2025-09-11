import marimo

__generated_with = "0.15.3"
app = marimo.App(width="medium", app_title="Pydantic Agent")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from web_setup import setup

    setup()
    return


@app.cell
def _(mo):
    import base64

    from pydantic_ai.messages import BinaryContent

    def get_class(input):
        return getattr(input, "__class__", type("Unknown", (), {})).__name__

    def display_agent_output(result):
        images = []

        for msg_i, msg in enumerate(result.new_messages(), start=1):
            msg_type = get_class(msg)
            print(f"\n=== Message {msg_i}: {msg_type} ===")

            for part_i, part in enumerate(getattr(msg, "parts", []), start=1):
                part_type = get_class(part)
                print(f"  Part {part_i}: {part_type}")

                content = getattr(part, "content", None)
                if isinstance(content, list):
                    for item_i, item in enumerate(content, start=1):
                        item_type = get_class(item)
                        print(f"    Item {item_i}: {item_type}")
                        if isinstance(item, BinaryContent) and item.is_image:
                            # Convert binary data to base64 data URI for marimo
                            image_b64 = base64.b64encode(item.data).decode("utf-8")
                            data_uri = f"data:image/png;base64,{image_b64}"
                            images.append(mo.image(src=data_uri))
                            print("      → Image displayed below")
                        elif isinstance(item, str):
                            print(f"      Text: {item}")
                elif isinstance(content, BinaryContent) and content.is_image:
                    print("    Content: BinaryContent (image)")
                    # Convert binary data to base64 data URI for marimo
                    image_b64 = base64.b64encode(content.data).decode("utf-8")
                    data_uri = f"data:image/png;base64,{image_b64}"
                    images.append(mo.image(src=data_uri))
                    print("      → Image displayed below")
                elif isinstance(content, str):
                    print(f"    Content: Text → {content}")

                # Direct text parts (like TextPart.text)
                if hasattr(part, "text") and part.text:
                    print(f"    Part.text: {part.text}")

        # Return images so marimo can display them
        if images:
            return mo.vstack(images)
        return None

    return (display_agent_output,)


@app.cell
async def _(display_agent_output):
    from pydantic_agent import Dependencies
    from pydantic_agent import agent as writer_agent
    from pydantic_ai import RunContext

    @writer_agent.instructions
    async def add_story_uuid(ctx: RunContext[str]) -> str:
        return f"Story UUID: {ctx.deps.story_uuid}."

    deps = Dependencies(story_uuid="067527ac-0ee5-4fe9-ad51-b316b12d5cc1")
    prompt = (
        "Generate a new illustration for page 1.\n"
        "Use a watercolor style.\n"
        "The page content should be at the bottom of the image, in text format."
    )
    result = await writer_agent.run(prompt, deps=deps)
    print(result.output)
    display_agent_output(result)
    return Dependencies, deps, writer_agent


@app.cell
async def _(deps, display_agent_output, writer_agent):
    result_1 = await writer_agent.run("what's on page 1?  what about the image?", deps=deps)
    display_agent_output(result_1)
    return


@app.cell
async def _(Dependencies, writer_agent):
    from apps.ai.models import Conversation

    conv = Conversation.objects.filter(user_id=1).first()
    deps_1 = Dependencies(story_uuid="067527ac-0ee5-4fe9-ad51-b316b12d5cc1")
    result_2 = await writer_agent.run("what's on page 1?", deps=deps_1)
    conv.add_run(result_2)
    return conv, deps_1, result_2


# @app.cell
# def _(conv):
#     conv.history
#     return


@app.cell
async def _(deps_1, result_2, writer_agent):
    await writer_agent.run(
        "what did i just ask you to help me with?", deps=deps_1, message_history=result_2.all_messages()
    )
    return


@app.cell
def _(result_2):
    messages = result_2.all_messages()
    for msg in messages:
        print(f"Message: {msg}")
        for part in msg.parts:
            print(f"Part: {part}")
    return


if __name__ == "__main__":
    app.run()
