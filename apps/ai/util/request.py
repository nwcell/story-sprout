# app/utils/ai_request.py
from functools import wraps
from time import monotonic

from django.db import transaction

from apps.ai.models import AIRequest


# TODO: Make this work
def ai_request_task(func):
    @wraps(func)
    def wrapper(request_uuid: str, *args, **kwargs):
        t0 = monotonic()
        with transaction.atomic():
            req = AIRequest.objects.select_for_update().get(uuid=request_uuid)
            req.status = AIRequest.Status.RUNNING
            req.save(update_fields=["status"])
        try:
            out, extra_updates = func(req, *args, **kwargs)
            # func returns (output_text, {optional extra fields})
            updates = {
                "status": AIRequest.Status.SUCCESS,
                "output_text": out,
                "runtime_ms": int((monotonic() - t0) * 1000),
            }
            if extra_updates:
                updates.update(extra_updates)
            for k, v in updates.items():
                setattr(req, k, v)
            req.save(update_fields=sorted(updates.keys()))
            return out
        except Exception as e:
            req.error_message = str(e)
            req.status = AIRequest.Status.FAILED
            req.runtime_ms = int((monotonic() - t0) * 1000)
            req.save(update_fields=["error_message", "status", "runtime_ms"])
            raise

    return wrapper
