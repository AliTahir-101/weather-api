import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings


class WeatherView(APIView):
    def get(self, request, city_name):
        api_url = f"{settings.OPENWEATHERMAP_API_URL}?q={city_name}&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(api_url)
        data = response.json()
        return Response(data)
