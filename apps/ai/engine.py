import os

import litellm
from django.conf import settings
from django.template import Context, Template


def render_prompt(template_name: str, context: dict):
    # Get absolute path to the template file
    template_path = os.path.join(settings.BASE_DIR, "apps/ai/prompt_templates", template_name)

    # Read file contents directly
    with open(template_path) as f:
        template_content = f.read()

    # Manually create and render template
    template = Template(template_content)
    return template.render(Context(context))


class AIEngine:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.temperature = 0.7

    def completion(self, prompt: str, stream: bool = False) -> str:
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=stream,
        )
        return response.choices[0].message.content

    def prompt_completion(self, template_name: str, context: dict, stream: bool = False) -> str:
        prompt = render_prompt(template_name, context)
        print(prompt)
        return self.completion(prompt, stream=stream)
