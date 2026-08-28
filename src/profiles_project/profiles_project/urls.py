from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('profiles_api.urls')),
    path('api/v1/', include('profiles_api.urls')),

    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),

    path(
        'static/<path:path>',
        serve,
        {'insecure': True},
    ),
]
