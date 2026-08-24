from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('profiles_api.urls')),
    path('api/v1/', include('profiles_api.urls')),
    path(
        'static/<path:path>',
        serve,
        {'insecure': True},
    ),
]
