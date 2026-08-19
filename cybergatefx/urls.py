"""Root URL configuration for CybergateFX."""
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom admin dashboard lives at /admin/ (it replaces the default index page).
from bookings.admin_dashboard import admin_dashboard_view


def health(_request):
    """Lightweight liveness/readiness probe for Render.

    Returns 200 if the database responds to a trivial query, 503 otherwise.
    Intentionally minimal — no auth, no secrets — so uptime monitors can
    hit it cheaply.
    """
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return JsonResponse({"status": "ok"})
    except Exception as exc:  # pragma: no cover — surfaced to the caller
        return JsonResponse({"status": "degraded", "error": str(exc)}, status=503)


urlpatterns = [
    path('health/', health, name='health'),

    # Admin: custom dashboard at root of /admin/, then include the real admin.
    path('admin/', admin_dashboard_view, name='admin_dashboard'),
    path('admin/portal/', admin.site.urls),

    # Public + customer-facing
    path('', include('mentors.urls')),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),
]

# Serve uploaded media in development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
