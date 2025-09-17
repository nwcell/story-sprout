import logging
import os
from dataclasses import dataclass

import litellm
from django.conf import settings
from django.template import Context, Template
from pydantic_ai import Agent

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


@dataclass
class WriterDeps:
    api_key: str


writer_agent = Agent(
    "openai:gpt-4o",
    deps_type=int,
    output_type=bool,
    system_prompt=("You are a childrens book ghost author.  You are helping ghostwrite childrens stories."),
)


class AIEngine:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.image_model = "dall-e-3"
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
        logger.info(f"AIEngine: completion response: {response}")
        logger.info(f"AIEngine: completion response content: {response.choices[0].message.content}")
        return response.choices[0].message.content

    def prompt_completion(self, template_name: str, context: dict, stream: bool = False) -> str:
        prompt = render_prompt(template_name, context)
        logger.info(f"AIEngine: prompt_completion prompt: {prompt}")
        return self.completion(prompt, stream=stream)

    def generate_image(self, prompt: str) -> str | None:
        response = litellm.image_generation(
            model=self.image_model, prompt=prompt, size="1024x1024", quality="auto", n=1
        )
        return response.data[0].url
