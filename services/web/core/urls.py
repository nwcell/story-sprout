from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_http_methods

from .api import api


@require_http_methods(["GET"])
def healthcheck(request):
    """Simple healthcheck endpoint to verify server is running"""
    return JsonResponse({"status": "healthy", "message": "Django server is running"})


urlpatterns = [
    path("healthcheck/", healthcheck, name="healthcheck"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    # path("events/", include(django_eventstream.urls)),
    path("", include("apps.landing.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("stories/", include("apps.stories.urls")),
    path("subscriptions/", include("apps.subscriptions.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    # Catch legacy livereload requests and return 204 to stop spam
    # path("livereload/<path:path>", lambda request, path: JsonResponse({}, status=204)),
    path("api/", api.urls),
    path("mcp/", include("mcp_server.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
