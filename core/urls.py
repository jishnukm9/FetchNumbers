from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.upload_screenshot, name='upload_screenshot'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
