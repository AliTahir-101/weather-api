from rest_framework.views import APIView
from rest_framework.response import Response


class WeatherView(APIView):
    def get(self, request, city_name):
        return Response({"message": f"We will show details for city {city_name} here!"})
