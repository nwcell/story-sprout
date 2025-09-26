from django import template
from django.utils.safestring import mark_safe

from markdownx.utils import markdownify

register = template.Library()


@register.filter(name="markdown_to_html")
def markdown_to_html(value: str | None) -> str:
    """Render a Markdown string as HTML."""
    if not value:
        return ""
    rendered = markdownify(value)
    return mark_safe(rendered)
