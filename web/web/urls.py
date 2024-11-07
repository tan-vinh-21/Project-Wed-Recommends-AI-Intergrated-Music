from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include('music.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
