from ninja import Router

from apps.ai.schemas import JobStatus, StoryJob
from apps.ai.util.celery import enqueue_job

router = Router()


# TODO: Add Auth
@router.post("/jobs/story-title")
def create_story_title_job(request, payload: StoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_title",
        payload=payload,  # JSON serializable
        # params={"args": **payload.dict()},  # JSON serializable
    )
    return {"job_uuid": str(job.uuid), "status": job.status}
