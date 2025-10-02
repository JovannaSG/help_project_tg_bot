from datetime import datetime
import math
import requests


class WeatherService:
    def __init__(self):
        self.code_to_smile: dict[str, str] = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

    async def get_weather_forecast(self, city_name: str) -> str | None:
        """Ваша функция получения погоды, переведенная в асинхронный стиль"""
        try:
            # Делаем запрос для получения прогноза погоды
            response = requests.get(
                "http://api.openweathermap.org/data/2.5/weather?q={}&lang=ru&units=metric&appid=4ba714d9111450e5537f17134b7235e4"
                .format(city_name)
            )
            
            if response.status_code != 200:
                return None

            # Парсим данные из json
            data = response.json()
            city = data["name"]
            cur_temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]

            sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"])
            sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"])
            length_of_the_day = datetime.fromtimestamp(data["sys"]["sunset"]) \
                - datetime.fromtimestamp(data["sys"]["sunrise"])
            weather_description = data["weather"][0]["main"]

            if weather_description in self.code_to_smile:
                wd = self.code_to_smile[weather_description]
            else:
                wd = "Посмотри в окно, не пойму что там"

            # Формируем текст прогноза
            weather_text = (
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Погода в городе: {city}\nТемпература: {cur_temp}°C {wd}\n"
                f"Влажность: {humidity}%\n"
                f"Давление: {math.ceil(pressure/1.333)} мм.рт.ст\n"
                f"Ветер: {wind} м/с \n"
                f"Восход солнца: {sunrise_timestamp}\n"
                f"Закат солнца: {sunset_timestamp}\n"
                f"Продолжительность дня: {length_of_the_day}\n"
                f"Хорошего дня!"
            )
            
            return weather_text
        except Exception as e:
            return None


# Глобальный экземпляр сервиса погоды
weather_service = WeatherService()
