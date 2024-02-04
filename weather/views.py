import httpx
import asyncio
from adrf.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.shortcuts import render
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from weather.serializers import WeatherSerializer
from django.utils.translation import get_language_from_request, activate, gettext as _


def landing_page(request):
    context = {
        'project_name': 'Weather API',
        'author': 'Ali Tahir',
    }
    return render(request, 'weather/landing_page.html', context)


class WeatherView(APIView):
    """
    This view retrieves weather data from the OPENWEATHERMAP_API for a specified city.

    - `city_name`: The name of the city for which weather data is requested.
    """
    @swagger_auto_schema(
        operation_description="Retrieve weather data for a specified city.",
        manual_parameters=[
            openapi.Parameter('city_name', openapi.IN_PATH,
                              description="The name of the city.", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('200 OK', WeatherSerializer(),
                                  examples={
                                  'application/json': {
                                      "city_name": "Helsinki",
                                      "temperature": -0.39,
                                      "min_temperature": -1.67,
                                      "max_temperature": 0.98,
                                      "humidity": 85,
                                      "pressure": 998,
                                      "wind_speed": 12.07,
                                      "wind_direction": "Southwest",
                                      "description": "clear sky"
                                  }}),
            400: "Bad Request: The provided city_name parameter is invalid.",
            403: "Forbidden: Access to this resource is not allowed.",
            404: "Not Found: The requested city was not found.",
            500: "Internal Server Error: An unexpected error occurred.",
            503: "Service Unavailable: The API server is currently unavailable."
        }
    )
    async def get(self, request, city_name):
        return await self.retrieve_weather_data(request, city_name)

    async def retrieve_weather_data(self, request, city_name, lang_code=None):
        """
        Retrieve weather data for the specified city.

        Parameters:
        - `city_name`: The name of the city.
        - `lang_code` (Optional): Response Language Code (e.g. en, ur, ar).

        Returns:
        - Weather data including temperature, humidity, wind speed, etc. (in metric units).
        """
        try:
            if city_name:
                city_name = city_name.lower()
            if lang_code:
                lang_code = lang_code.lower()
            else:
                lang_code = get_language_from_request(request)

            cache_key = f'weather_data_{city_name}_{lang_code}' if lang_code else f'weather_data_{city_name}'
            cached_weather = cache.get(cache_key)

            if cached_weather:
                return Response(cached_weather)

            if lang_code:
                activate(lang_code)

            api_url = f"{settings.OPENWEATHERMAP_API_URL}?q={city_name}&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url)
                response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

            data = response.json()

            # Extract the relevant information from the API response
            weather_data = data.get("main", {})
            weather_description = data.get("weather", [{}])[0]

            city_info = {
                _("city_name"): _(city_name),
                _("temperature"): weather_data.get("temp"),
                _("min_temperature"): weather_data.get("temp_min"),
                _("max_temperature"): weather_data.get("temp_max"),
                _("humidity"): weather_data.get("humidity"),
                _("pressure"): weather_data.get("pressure"),
                _("wind_speed"): data.get("wind", {}).get("speed"),
                _("wind_direction"): _(self.get_wind_direction(data.get("wind", {}).get("deg", -1))),
                _("description"): _(weather_description.get("description", "Not Available!"))
            }

            # Cache the result before returning
            cache.set(cache_key, city_info, settings.WEATHER_CACHE_TIMEOUT)

            return Response(city_info)

        except httpx.NetworkError as e:
            # Handle network errors
            return Response({"error": _("Failed to establish a connection to the API server. Please check your internet connection and try again.")}, status=503)

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (e.g., 404, 500)
            return Response({"error": _(f"API request returned an error: {e.response.status_code}. Please check your request and try again.")}, status=e.response.status_code)

        except httpx.RequestError as e:
            # Handle general httpx request exceptions
            return Response({"error": _("Failed to retrieve data from the API. Please try again later.")}, status=500)

        except asyncio.TimeoutError as e:
            # Handle asyncio-specific timeouts
            return Response({"error": _("The request timed out. Please try again later.")}, status=504)

        except Exception as e:
            # Handle other unexpected exceptions
            return Response({"error": _("An unexpected error occurred. Please try again later.")}, status=500)

    def get_wind_direction(self, degrees):
        # Map wind direction based on degrees
        if degrees == -1:
            return "Not Available!"
        if 22.5 <= degrees < 67.5:
            return "Northeast"
        elif 67.5 <= degrees < 112.5:
            return "East"
        elif 112.5 <= degrees < 157.5:
            return "Southeast"
        elif 157.5 <= degrees < 202.5:
            return "South"
        elif 202.5 <= degrees < 247.5:
            return "Southwest"
        elif 247.5 <= degrees < 292.5:
            return "West"
        elif 292.5 <= degrees < 337.5:
            return "Northwest"
        else:
            return "North"


class WeatherViewWithLang(WeatherView):
    """
    This view retrieves weather data from the OPENWEATHERMAP_API for a specified city with language code.

    - `city_name`: The name of the city for which weather data is requested.
    - `lang_code`: Response Language Code (e.g. en, ur, ar).
    """
    @swagger_auto_schema(
        operation_description="Retrieve weather data for a specified city with language code.",
        manual_parameters=[
            openapi.Parameter('city_name', openapi.IN_PATH,
                              description="The name of the city.", type=openapi.TYPE_STRING),
            openapi.Parameter('lang_code', openapi.IN_PATH,
                              description="Response Language Code (e.g. en, ur, ar).", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('200 OK', WeatherSerializer(),
                                  examples={
                                  'application/json': {
                                      "شہر کا نام": "کراچی",
                                      "درجہ حرارت": 25.9,
                                      "کم سے کم درجہ حرارت": 25.9,
                                      "زیادہ سے زیادہ درجہ حرارت": 25.9,
                                      "نمی": 41,
                                      "دباؤ": 1014,
                                      "ہوا کی رفتار": 9.26,
                                      "ہوا کی سمت": "جنوب مشرق",
                                      "تفصیل": "دھواں"
                                  }}),
            400: "Bad Request: The provided city_name parameter is invalid.",
            403: "Forbidden: Access to this resource is not allowed.",
            404: "Not Found: The requested city was not found.",
            500: "Internal Server Error: An unexpected error occurred.",
            503: "Service Unavailable: The API server is currently unavailable."
        }
    )
    async def get(self, request, city_name, lang_code=None):
        return await super().retrieve_weather_data(request, city_name, lang_code)
