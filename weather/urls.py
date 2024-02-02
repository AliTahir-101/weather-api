from django.urls import path
from .views import WeatherView

urlpatterns = [
    path('current/<str:city_name>/', WeatherView.as_view(), name='current-weather'),
    # This path now becomes accessible at /api/v1/weather/current/<our_city_name>/
]
