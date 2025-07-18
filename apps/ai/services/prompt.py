from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from ..models import AIWorkflow, AiJob

def generate_prompt(template_name: str, context: dict):
    template = get_template(template_name)
    return template.render(context)

def orchestrate(target_ct: ContentType, target_id: int, workflow_func: str, user=None):
    workflow = AIWorkflow.objects.create(
        target_ct=target_ct,
        target_id=target_id,
        workflow_func=workflow_func,
        user=user,
    )

    func = globals()[workflow_func]
    func(workflow)
    

def page_content_workflow(workflow: AIWorkflow):
    page = workflow.target
    prompt = generate_prompt("page_content.md", {"page": page})
    
    job = AiJob.objects.create(
        workflow=workflow,
        prompt_payload=prompt,
    )
    
    # Mark as running and process the prompt
    job.mark_as_running()
    
    try:
        # TODO: Replace with actual AI service call
        # For now, just simulate a successful response
        result = f"This is page {page.page_number} of '{page.story.title}'."
        
        # Update page content with the generated result
        page.content = result
        page.content_generating = False
        page.save(update_fields=['content', 'content_generating'])
        
        # Mark job as succeeded
        job.mark_as_succeeded(prompt_result=result)
        
        return job
    except Exception as e:
        job.mark_as_failed(str(e))
        raise
