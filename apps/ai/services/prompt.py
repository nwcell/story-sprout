from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from .models import AIWorkflow, AiJob

def generate_prompt(template_name: str, context: dict):
    template = get_template(template_name)
    return template.render(context)

def orchestrate(target_ct: ContentType, target_id: int, workflow_func: str, workflow_payload: dict = {}):
    if not workflow_payload:
        workflow_payload = {}
    
    workflow = AIWorkflow.objects.create(
        target_ct=target_ct,
        target_id=target_id,
        workflow_func=workflow_func,
        workflow_payload=workflow_payload,
    )

    func = locals()[workflow_func]
    func(workflow, workflow_payload)
    

def page_content_workflow(workflow: AIWorkflow, workflow_payload: dict):
    page = workflow.target
    prompt = generate_prompt("page_content.md", {
        "page": page, 
        **workflow_payload
    })
    print(prompt)
    # job = AiJob.objects.create(
    #     workflow=workflow,
    #     prompt_payload=prompt,
    # )
