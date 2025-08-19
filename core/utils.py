from django.template.loader import render_to_string


def append_content(response, template, context: dict | None = None, oob: bool = False):
    """
    Append content from template to an HttpResponse object.
    """
    # Render new template with OOB flag
    if context is None:
        context = {}
    context["oob"] = oob
    rendered = render_to_string(template, context)

    # Convert both to strings, then back to bytes
    current_content = response.content.decode("utf-8")
    new_content = current_content + rendered
    response.content = new_content.encode("utf-8")
    return response
