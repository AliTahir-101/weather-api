import pytest
import asyncio
from django.test import RequestFactory
from httpx import Request, Response, NetworkError, RequestError
from unittest.mock import patch, AsyncMock
from weather.views import WeatherViewWithLang
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache_before_tests():
    """
    A fixture that clears the Django cache before each test runs.

    This ensures that each test starts with a clean state, without any cached data
    from previous tests that might affect the outcomes.
    """
    cache.clear()


class TestWeatherViewWithLang:
    """
    This class contains tests for the WeatherViewWithLang.

    It tests the async retrieval of weather data based on a city name.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        Sets up the test environment for each test method.

        Initializes variables with city name, test URL, and creates a RequestFactory instance
        for generating request objects. It also prepares a mock HTTPX request object for use in mocking responses.
        """
        self.test_city_name = 'helsinki'
        self.lang_code = 'en'
        self.test_url = f'/api/v1/weather/current/{self.test_city_name}'
        self.factory = RequestFactory()
        self.django_request = self.factory.generic('GET', self.test_url)
        self.httpx_request = Request(
            method="GET",
            url=f"https://example.com/api/v1/weather/current/{self.test_city_name}",
            cookies={"Cookie": "cookie_value"}
        )

    @pytest.fixture
    def mock_successful_response_api(self):
        """
        Provides a mock response mimicking a successful API call to an external weather service.

        This mock response includes weather data such as temperature, humidity, pressure, etc.
        """
        return {
            "main": {
                "temp": 25.9,
                "temp_min": -1.67,
                "temp_max": 0.98,
                "humidity": 85,
                "pressure": 998,
            },
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 12.07, "deg": 202.5},
        }

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_success(self, mock_successful_response_api):
        """
        Tests successful weather data retrieval for a given city.

        Parameters:
        - mock_successful_response_api: A fixture providing mock API response data.

        This test mocks the external API response to ensure the view correctly processes and returns
        the expected weather data.
        """
        # Mocking the HTTPX response to simulate an external API returning successful weather data
        mock_response = Response(
            200, json=mock_successful_response_api, request=self.httpx_request)

        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            # Pass the simulated request and city_name to the view
            response = await WeatherViewWithLang().get(self.django_request, city_name=self.test_city_name, lang_code=self.lang_code)
            # Assertions to verify the view responds with the correct status and data
            assert response.status_code == 200
            assert "temperature" in response.data
            assert response.data["temperature"] == mock_successful_response_api["main"]["temp"]
            assert response.data["humidity"] == mock_successful_response_api["main"]["humidity"]
            assert response.data["pressure"] == mock_successful_response_api["main"]["pressure"]

    @pytest.mark.parametrize("degrees, expected_direction", [
        (0, "North"),
        (22.5, "Northeast"),
        (45, "Northeast"),
        (67.4, "Northeast"),
        (67.5, "East"),
        (90, "East"),
        (112.4, "East"),
        (112.5, "Southeast"),
        (157, "Southeast"),
        (180, "South"),
        (202, "South"),
        (247, "Southwest"),
        (270, "West"),
        (292, "West"),
        (337, "Northwest"),
        (360, "North"),
        (-1, "Not Available!"),
        (999, "North"),  # Testing out of normal range, assuming it wraps
    ])
    def test_get_wind_direction(self, degrees, expected_direction):
        """
        Test the get_wind_direction method for various degrees.

        This test verifies that the get_wind_direction method correctly calculates
        the wind direction based on the provided wind degrees. It covers all directional
        ranges and special cases to ensure comprehensive coverage and accuracy of the method.

        Parameters:
        - degrees: The wind direction in degrees for which the method calculates the cardinal direction.
        - expected_direction: The expected cardinal direction based on the provided degrees.
        """
        view = WeatherViewWithLang()
        assert view.get_wind_direction(
            degrees) == expected_direction, f"Failed for degrees: {degrees}"

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_invalid_city(self):
        """
        Tests the behavior of the WeatherViewWithLang when an invalid city name is provided.

        This test simulates an external API response with a 404 status code, indicating
        that the specified city could not be found. It verifies that the WeatherViewWithLang
        correctly handles this scenario by returning a 404 status code.
        """
        city_name = 'InvalidCity'
        mock_response = Response(
            404, json={}, request=self.httpx_request)

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = mock_response

            # Pass the Django HttpRequest object to the view
            response = await WeatherViewWithLang().get(self.django_request, city_name, self.lang_code)
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_api_error(self):
        """
        Tests the WeatherViewWithLang's handling of an API error.

        This test simulates an external API response with a 500 status code, indicating
        an internal server error on the API's end. It verifies that the WeatherViewWithLang
        appropriately handles this scenario by returning a 500 status code.
        """
        mock_response = Response(
            500, json={}, request=self.httpx_request)
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = mock_response
            response = await WeatherViewWithLang().get(self.httpx_request, self.test_city_name, self.lang_code)
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_network_error(self):
        """
        Tests the WeatherViewWithLang's response to a network error during the API call.

        This test simulates a network error by raising a NetworkError exception when
        the external API is called. It verifies that the WeatherViewWithLang correctly handles
        network errors by returning a 503 Service Unavailable status code and includes
        an error message in the response.
        """
        with patch('httpx.AsyncClient.get', side_effect=NetworkError("Test Network Error")) as mock_get:
            response = await WeatherViewWithLang().get(self.django_request, self.test_city_name, self.lang_code)
            assert response.status_code == 503
            assert "error" in response.data

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_request_error(self):
        """
        Tests the WeatherViewWithLang's response to a RequestError during the API call.

        This test simulates a RequestError by raising it when the external API is called.
        It verifies that the WeatherViewWithLang correctly handles RequestError by returning a specific
        status code and includes an error message in the response. This ensures the application
        can gracefully handle issues with the outgoing request, such as network problems or
        DNS lookup failures.
        """
        # Simulate a RequestError to be raised by the httpx client
        with patch('httpx.AsyncClient.get', side_effect=RequestError("Test Request Error")) as mock_get:
            response = await WeatherViewWithLang().get(self.django_request, self.test_city_name, self.lang_code)
            assert response.status_code == 500
            assert "error" in response.data
            assert response.data["error"] == "Failed to retrieve data from the API. Please try again later."

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_timeout_error(self):
        """
        Tests the WeatherViewWithLang's response to an asyncio.TimeoutError during the API call.

        This test simulates a scenario where the external API call does not complete within
        an expected timeframe, raising an asyncio.TimeoutError. It verifies that the WeatherViewWithLang
        correctly handles the timeout error by returning a specific status code and includes an
        appropriate error message in the response. This ensures the application can inform the user
        properly when a request timeout occurs.
        """
        # Simulate an asyncio.TimeoutError to be raised during the API call
        with patch('httpx.AsyncClient.get', side_effect=asyncio.TimeoutError("Test Timeout Error")) as mock_get:
            response = await WeatherViewWithLang().get(self.django_request, self.test_city_name, self.lang_code)
            # Verify that view handles asyncio.TimeoutError and sets a custom response status code and message
            # Gateway Timeout status code
            assert response.status_code == 504
            assert "error" in response.data
            assert response.data["error"] == "The request timed out. Please try again later."

    @pytest.mark.asyncio
    async def test_retrieve_weather_data_caching(self, mock_successful_response_api):
        cache_key = f'weather_data_{self.test_city_name}_en'

        # Perform the first request to populate the cache
        await self.test_retrieve_weather_data_success(mock_successful_response_api)

        # Mock the HTTP client to raise an exception if called again, ensuring cache is used
        with patch('httpx.AsyncClient.get', side_effect=Exception("API should not be called")):
            response = await WeatherViewWithLang().get(self.django_request, city_name=self.test_city_name, lang_code=self.lang_code)
            assert response.status_code == 200
            # Verify the response is identical to the mock_successful_response_api
            assert response.data["temperature"] == mock_successful_response_api["main"]["temp"]

        # Verify cache is populated
        cached_response = cache.get(cache_key)
        assert cached_response is not None
        assert cached_response["temperature"] == mock_successful_response_api["main"]["temp"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("description, lang_code, keys_translation", [
        (
            "Test With lang Code: En - English",
            "en",
            {
                "temp": "temperature",
                "humidity": "humidity",
                "pressure": "pressure"
            }
        ),
        (
            "Test With lang Code: Ur - Urdu",
            "ur",
            {
                "temp": "درجہ حرارت",
                "humidity": "نمی",
                "pressure": "دباؤ",
                "temp_min": "کم سے کم درجہ حرارت"
            }
        )
    ])
    async def test_retrieve_weather_data_with_lang_code(self, description, lang_code, keys_translation, mock_successful_response_api):
        """
        Tests the WeatherViewWithLang's ability to retrieve weather data with language-specific keys.

        This test uses parameterization to run the same test logic with different language codes and expected key translations. 
        It simulates a successful API response and verifies that the weather data returned by the view uses the correct 
        language-specific keys based on the provided lang_code parameter.

        Parameters:
        - description: A string describing the test case, useful for distinguishing test scenarios.
        - lang_code: The language code to request weather data for ('en' for English, 'ur' for Urdu, etc.).
        - keys_translation: A dictionary mapping generic weather data keys to their language-specific translations.
        - mock_successful_response_api: A fixture providing mock API response data.

        The test asserts that the response data uses the correct translations for temperature, humidity, and pressure keys,
        validating the view's ability to handle multilingual responses.
        """
        # Mocking the HTTPX response to simulate an external API returning successful weather data
        mock_response_en = Response(
            200, json=mock_successful_response_api, request=self.httpx_request)

        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_en
            response = await WeatherViewWithLang().get(self.django_request, city_name=self.test_city_name, lang_code=lang_code)
            assert response.status_code == 200
            # Asserting that the response data keys are correctly translated based on the lang_code
            for key, translation in keys_translation.items():
                assert response.data[translation] == mock_successful_response_api["main"][key], description
