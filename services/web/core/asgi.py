"""
ASGI config for core project.

Co-hosts Django and the MCP server in the same runtime:
  - Django at `/`
  - MCP at `/mcp`

Run with your normal ASGI server (uvicorn/daphne/gunicorn+uvicorn worker).
"""

import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount

from mcp_service.server import mcp

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()


# Django ASGI app
django_asgi = get_asgi_application()

# MCP ASGI app (defined in services/web/mcp/app.py)

# Compose: Starlette routes `/mcp` to MCP, everything else to Django
application = Starlette(
    routes=[
        Mount("/mcp", app=mcp.streamable_http_app()),
        Mount("/", app=django_asgi),
    ]
)
