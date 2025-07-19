from django.contrib.contenttypes.models import ContentType
from ..models import AIWorkflow
from ..tasks import page_content_workflow

def orchestrate(target_ct: ContentType, target_id: int, workflow_func: str, user=None):
    workflow = AIWorkflow.objects.create(
        target_ct=target_ct,
        target_id=target_id,
        workflow_func=workflow_func,
        user=user,
    )
    
    if workflow_func == 'page_content_workflow':
        page_content_workflow.delay(workflow.id)
    


