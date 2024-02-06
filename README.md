# 🌦️ Weather API - Multilingual and Asynchronous Support

## 🌐 Overview

The Weather API provides current weather information for any city using the OpenWeatherMap API, supporting multiple languages (en, ur, ar) via the 'Accept-Language' header or 'lang_code' URL parameter. It leverages asynchronous network calls for enhanced performance under high load or when fetching data from slow external APIs, enabling concurrent request handling and reduced wait times for consumers.

## 🚀 Demo

Check out the live demo of the Weather API here: [Weather API Live Demo](https://weather-api-demo-11d5de3423f4.herokuapp.com/)

## Features

- 🌦️ Provides current weather information for any city.
- 🌍 Supports multiple cities worldwide.
- 🌡️ Returns temperature, min. temperature, max. temperature, humidity, and more.
- 💨 Includes wind speed and direction (e.g north, south, west, east).
- ☁️ Provides weather descriptions (e.g., clear sky, cloudy).
- 🌐 Supports multiple languages: English (default), and two additional languages (Urdu and Arabic).
- ⏳ Caches results for efficient performance (configurable caching time).
- 🪄 Gracefully handles failures and provides meaningful error responses.
- 🚀 Utilizes asyncio for handling network calls, enhancing performance.
- 📜 Compliant with the OpenAPI Specification for API documentation.
- 🐳 Fully containerized with Docker and Docker Compose for easy deployment.

## Prerequisites

Before running this project, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

1. **Clone the Repository:**

   ```bash
   git@github.com:AliTahir-101/weather-api.git
   cd weather-api
   ```

2. **Environment Setup:**
   Create a `.env` file in the root directory and add any necessary environment variables e.g.

   ```bash
   OPENWEATHERMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   OPENWEATHERMAP_API_URL=http://api.openweathermap.org/data/2.5/weather
   DEBUG=True # For Dev
   REDIS_CACHE_URL=redis://redis:6379/1 # without docker use redis://127.0.0.1:6379/1
   SECRET_KEY='django-insecure-%q*r!c-7xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxw9-'
   ALLOWED_HOSTS='localhost,127.0.0.1' # For Dev
   ```

3. **Build and Run with Docker Compose:**

   ```bash
   docker-compose down --remove-orphans (Stopping and Removing Previous Containers (Optional))

   docker-compose up --build
   ```

## 📡 API Endpoints

- `/api/v1/weather/current/<city_name>`: Get current weather data for a specific city.
- `/api/v1/weather/current/<city_name>/<lang_code>`: Get current weather data for a specific city and language.
- `/swagger/`: Interactive API documentation that lets you try out the API endpoints directly from your browser.
- `/redoc/`: Alternative API documentation for a more detailed overview of the API structure and its endpoints.

## 📋 API Usage

To use the API, make a GET request to the `/api/v1/weather/current/<city_name>` endpoint with the desired city name as a parameter.

Example Request:

```bash
http://127.0.0.1:8000/api/v1/weather/current/helsinki
```

Example Response:

```json
{
  "city_name": "helsinki",
  "temperature": -0.39,
  "min_temperature": -1.67,
  "max_temperature": 0.98,
  "humidity": 85,
  "pressure": 998,
  "wind_speed": 12.07,
  "wind_direction": "Southwest",
  "description": "clear sky"
}
```

You can also make a GET request to the `/api/v1/weather/current/<city_name>/<lang_code>` endpoint with the desired city name along with desired lang code currently it supports only (en, ar, ur).

Example Request:

```bash
http://127.0.0.1:8000/api/v1/weather/current/karachi/ur
```

Example Response:

```json
{
  "شہر کا نام": "کراچی",
  "درجہ حرارت": 25.9,
  "کم سے کم درجہ حرارت": 25.9,
  "زیادہ سے زیادہ درجہ حرارت": 25.9,
  "نمی": 41,
  "دباؤ": 1014,
  "ہوا کی رفتار": 9.26,
  "ہوا کی سمت": "جنوب مشرق",
  "تفصیل": "دھواں"
}
```

## Testing

To run tests, use the following command:

```bash
docker-compose down --remove-orphans (Stopping and Removing Previous Containers (Optional))
docker-compose run --rm  weather_api pytest --cov-report term-missing --cov=weather.views weather/tests/
```
