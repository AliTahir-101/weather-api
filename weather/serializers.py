from rest_framework import serializers


class WeatherSerializer(serializers.Serializer):
    """
    Serializer for weather data returned from the OpenWeatherMap API.
    """
    city_name = serializers.CharField()
    temperature = serializers.DecimalField(max_digits=5, decimal_places=2)
    min_temperature = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_temperature = serializers.DecimalField(max_digits=5, decimal_places=2)
    humidity = serializers.IntegerField()
    pressure = serializers.IntegerField()
    wind_speed = serializers.DecimalField(max_digits=5, decimal_places=2)
    wind_direction = serializers.CharField()
    description = serializers.CharField()
