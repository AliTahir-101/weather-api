import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from requests.exceptions import RequestException, ConnectionError, HTTPError


class WeatherView(APIView):
    def get(self, request, city_name):
        try:
            api_url = f"{settings.OPENWEATHERMAP_API_URL}?q={city_name}&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

            data = response.json()

            # Extract the relevant information from the API response
            city_info = {
                "city_name": city_name,
                "temperature": data["main"]["temp"],
                "min_temperature": data["main"]["temp_min"],
                "max_temperature": data["main"]["temp_max"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": self.get_wind_direction(data["wind"]["deg"]),
                "description": data["weather"][0]["description"]
            }

            return Response(city_info)

        except ConnectionError as e:
            # Handle connection errors
            return Response({"error": "Failed to establish a connection to the API server. Please check your internet connection and try again."}, status=503)

        except HTTPError as e:
            # Handle HTTP errors (e.g., 404, 500)
            return Response({"error": f"API request returned an error: {e.response.status_code}. Please check your request and try again."}, status=e.response.status_code)

        except RequestException as e:
            # Handle general request exceptions
            return Response({"error": "Failed to retrieve data from the API. Please try again later."}, status=500)

        except Exception as e:
            # Handle other unexpected exceptions
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=500)

    def get_wind_direction(self, degrees):
        # Map wind direction based on degrees
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
