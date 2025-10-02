import logging
import os

from django.conf import settings
from django.template import Context, Template

logger = logging.getLogger(__name__)


def render_prompt(template_name: str, context: dict):
    # Get absolute path to the template file
    template_path = os.path.join(settings.BASE_DIR, "apps/ai/prompt_templates", template_name)

    # Read file contents directly
    with open(template_path) as f:
        template_content = f.read()

    # Manually create and render template
    template = Template(template_content)
    return template.render(Context(context))
