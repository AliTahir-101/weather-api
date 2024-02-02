from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Weather API",
        default_version='v1',
        description="Provides current weather information for any city using the OpenWeatherMap API.",
        contact=openapi.Contact(email="alitahir231@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[path('api/v1/weather/', include('weather.urls'))]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/weather/', include('weather.urls')),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
