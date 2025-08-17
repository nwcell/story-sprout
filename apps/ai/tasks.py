"""
Celery tasks for AI services.
"""

import logging
import os

import litellm
from celery import shared_task
from django.conf import settings
from django.template import Context, Template

from apps.ai.models import AiJob, AIWorkflow

logger = logging.getLogger(__name__)


def generate_prompt(template_name: str, context: dict):
    # Get absolute path to the template file
    template_path = os.path.join(settings.BASE_DIR, "apps/ai/prompt_templates", template_name)

    # Read file contents directly
    with open(template_path) as f:
        template_content = f.read()

    # Manually create and render template
    template = Template(template_content)
    return template.render(Context(context))


@shared_task
def page_content_workflow(workflow_id):
    workflow = AIWorkflow.objects.get(id=workflow_id)
    page = workflow.target
    prompt = generate_prompt("page_content.md", {"page": page, "generation_type": "content"})

    job = AiJob.objects.create(
        workflow=workflow,
        prompt_payload=prompt,
    )

    job.mark_as_running()

    try:
        response = litellm.completion(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1000
        )

        text = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        cost = getattr(response.usage, "total_cost", 0)

        page.content = text
        page.content_generating = False
        page.save()

        job.mark_as_succeeded(prompt_result=text, usage_tokens=usage, cost_usd=cost)
        return {"job_id": job.id}

    except Exception as e:
        job.mark_as_failed(str(e))
        logger.exception(f"Error in page_content_workflow: {e}")
        raise
