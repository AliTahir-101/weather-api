from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Weather API - Multilingual and Asynchronous Support",
        default_version='v1',
        description="""
            Provides current weather information for any city using the OpenWeatherMap API. This API supports multiple languages, allowing consumers to request data in their preferred language avaiable options (en, ur, ar) using the 'Accept-Language' header or 'lang_code' URL parameter.
                    
            Additionally, this API leverages asynchronous network calls for enhanced performance, particularly under high load or when fetching data from slow external APIs. This means that the API is capable of handling a larger number of requests concurrently, reducing the wait time for each consumer.
        """,
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
