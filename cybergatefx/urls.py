"""Root URL configuration for CybergateFX."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom admin dashboard lives at /admin/ (it replaces the default index page).
from bookings.admin_dashboard import admin_dashboard_view

urlpatterns = [
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
