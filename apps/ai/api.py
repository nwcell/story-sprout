from django.core.exceptions import ValidationError
from ninja import ModelSchema, Router
from ninja.errors import HttpError

from apps.ai.models import AIRequest

router = Router()


class JobIn(ModelSchema):
    class Meta:
        model = AIRequest
        fields = [
            "workflow",
            "target_uuid",
            "input_params",
        ]


class JobOut(ModelSchema):
    class Meta:
        model = AIRequest
        fields = [
            "uuid",
            "user",
            "workflow",
            "target_uuid",
            "input_params",
            "status",
            "output_text",
            "error_message",
            "created_at",
            "completed_at",
        ]


@router.post("/jobs", response=JobOut)
def create_job(request, payload: JobIn):
    try:
        ai_request = AIRequest.create_for_target(
            user=request.user,
            workflow_name=payload.workflow,
            target_uuid=payload.target_uuid,
            input_params=payload.input_params,
        )
    except ValidationError as e:
        raise HttpError(422, e.message) from e
    return ai_request
