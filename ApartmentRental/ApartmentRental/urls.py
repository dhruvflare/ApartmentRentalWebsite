# Main project urls.py - ApartmentRental/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/', include('DBComm.urls')),
    
    # API Authentication (DRF built-in)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # API Documentation (optional)
    # path('docs/', include_docs_urls(title='Apartment Rental API')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)