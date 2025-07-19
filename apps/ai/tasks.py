"""
Celery tasks for AI services.
"""
from celery import shared_task
import logging
import litellm

from apps.ai.models import AIWorkflow, AiJob
from apps.ai.services.template_utils import generate_prompt

logger = logging.getLogger(__name__)

@shared_task
def page_content_workflow(workflow_id):
    workflow = AIWorkflow.objects.get(id=workflow_id)
    page = workflow.target
    prompt = generate_prompt("page_content.md", {"page": page})
    
    job = AiJob.objects.create(
        workflow=workflow,
        prompt_payload=prompt,
    )
    
    job.mark_as_running()
    
    try:
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        text = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        cost = getattr(response.usage, 'total_cost', 0)
        
        page.content = text
        page.content_generating = False
        page.save(update_fields=['content', 'content_generating'])
        
        job.mark_as_succeeded(prompt_result=text, usage_tokens=usage, cost_usd=cost)
        return {"job_id": job.id}
        
    except Exception as e:
        job.mark_as_failed(str(e))
        logger.exception(f"Error in page_content_workflow: {e}")
        raise