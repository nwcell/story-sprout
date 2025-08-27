"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

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
    path("", include("apps.landing.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("stories/", include("apps.stories.urls")),
    path("subscriptions/", include("apps.subscriptions.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    # Catch legacy livereload requests and return 204 to stop spam
    # path("livereload/<path:path>", lambda request, path: JsonResponse({}, status=204)),
    path("api/", api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
