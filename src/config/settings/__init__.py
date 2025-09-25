from pathlib import Path

import environ

from .base import *  # noqa: F401,F403

# Initialize django-environ for overlay selection
_env_loader = environ.Env()
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    _env_loader.read_env(_env_path)

_env = _env_loader("DJANGO_ENV", default="dev")

_mod = f"{__name__}.{_env}"

try:
    _m = __import__(_mod, fromlist=["*"])
except ModuleNotFoundError:
    _m = None


if _m:
    for _k in dir(_m):
        if _k.isupper():
            globals()[_k] = getattr(_m, _k)
