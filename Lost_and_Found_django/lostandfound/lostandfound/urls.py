from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('migrateflask.urls')),  # This will include all URLs from the 'main' app, including login, dashboard, etc.
    # You can add other URLs specific to your project here if needed
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

