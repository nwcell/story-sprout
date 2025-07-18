from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from ..models import AIWorkflow

def generate_prompt(template_name: str, context: dict):
    template = get_template(template_name)
    return template.render(context)

def orchestrate(target_ct: ContentType, target_id: int, workflow_func: str):
    workflow = AIWorkflow.objects.create(
        target_ct=target_ct,
        target_id=target_id,
        workflow_func=workflow_func,
    )

    func = globals()[workflow_func]
    func(workflow)
    

def page_content_workflow(workflow: AIWorkflow):
    page = workflow.target
    prompt = generate_prompt("page_content.md", {"page": page})
