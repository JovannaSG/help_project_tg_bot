import re
from typing import Any, LiteralString, Optional

from bs4 import BeautifulSoup
import requests


class GismeteoParser:
    def __init__(self) -> None:
        self.session = requests.Session()
        # Говорим сайту, что данные получает браузер, а не программа
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        # Словарь с досутпными городами
        self.cities: dict[str, str] = {
            "иркутск": "irkutsk-4787",
            "москва": "moscow-4368",
            "санкт-петербург": "sankt-peterburg-4079",
            "новосибирск": "novosibirsk-4690",
            "екатеринбург": "yekaterinburg-4517"
        }

    def get_city_url(self, city_identifier) -> LiteralString:
        """
        Получить URL для города по его идентификатору
        """

        # В идеале вернуть f"https://www.gismeteo.ru/{city_identifier}"
        return f"https://www.gismeteo.ru/"

    def parse_weather_data(self, html_content):
        """
        Парсинг HTML и извлечение данных о погоде
        """

        soup = BeautifulSoup(html_content, "html.parser")
        weather_data: dict[str, Any] = {}

        # Находим название города
        city_name = soup.find("a", class_="city").get_text(strip=True)
        weather_data["city_name"] = city_name

        # Находим блок с текущей погодой
        weather_block = soup.find("div", class_="weather-info")

        if not weather_block:
            return None

        # 1. Основная температура
        temp_elem = weather_block.find("temperature-value", {"value": True})
        if temp_elem:
            weather_data["temperature"] = float(temp_elem.get("value"))
            print("="*10, type(weather_data["temperature"]))
            weather_data["temperature_unit"] = temp_elem.get("from-unit", "c")

        # 2. Описание погоды
        description = weather_block.find("div", class_="description")
        if description:
            weather_data["description"] = description.get_text(strip=True)

        # 3. Температура по ощущению
        feels_like = weather_block.find("div", class_="item-label")
        if feels_like:
            feels_like_value = feels_like.find_next(
                "div",
                class_="item-value"
            )
            if feels_like_value:
                temp_val = feels_like_value.find(
                    "temperature-value",
                    {"value": True}
                )
                if temp_val:
                    weather_data["feels_like"] = temp_val.get("value")

        # 4. Ветер
        wind_label = weather_block.find("div", class_="item-label")
        if wind_label:
            wind_value = wind_label.find_next("div", class_="item-value")
            if wind_value:
                wind_text = wind_value.get_text(strip=True)
                weather_data["wind"] = wind_text

        # 5. Давление
        pressure_label = weather_block.find("div", class_="item-label")
        if pressure_label:
            pressure_value = pressure_label.find_next(
                "div",
                class_="item-value"
            )
            if pressure_value:
                pressure_val = pressure_value.find(
                    "pressure-value",
                    {"value": True}
                )
                if pressure_val:
                    weather_data["pressure"] = pressure_val.get("value")
                    weather_data["pressure_unit"] = pressure_val.get(
                        "from-unit",
                        "mmhg"
                    )

        # 6. Влажность
        humidity_label = weather_block.find(
            "div",
            class_="item-label"
        )
        if humidity_label:
            humidity_value = humidity_label.find_next(
                "div",
                class_="item-value"
            )
            if humidity_value:
                humidity_text = humidity_value.get_text(strip=True)
                # Извлекаем только цифры из текста влажности
                humidity_match = re.search(r"\d+", humidity_text)
                if humidity_match:
                    weather_data["humidity"] = humidity_match.group()

        # 7. Температура воды
        water_label = weather_block.find("div", class_="item-label")
        if water_label:
            water_value = water_label.find_next("div", class_="item-value")
            if water_value:
                water_val = water_value.find(
                    "temperature-value",
                    {"value": True}
                )
                if water_val:
                    weather_data["water_temperature"] = water_val.get("value")

        # 8. Г/м активность
        gm_label = weather_block.find("a", class_="weather-item-gm")
        if gm_label:
            gm_value = gm_label.find("div", class_="item-value")
            if gm_value:
                gm_text = gm_value.get_text(strip=True)
                # Извлекаем количество баллов
                gm_match = re.search(r"\d+", gm_text)
                if gm_match:
                    weather_data["geomagnetic_activity"] = gm_match.group()

        # 9. Прогноз по часам
        forecast_block = soup.find("div", class_="current-weather-forecast")
        if forecast_block:
            time_slots = []
            time_items = forecast_block.find_all("div", class_="row-item")

            for item in time_items:
                time_span = item.find("span")
                if time_span:
                    time_slots.append(time_span.get_text(strip=True))

            if time_slots:
                weather_data["hourly_forecast"] = time_slots

        return weather_data

    def get_weather(self, city_identifier) -> Optional[dict[str, Any]]:
        """
        Получить погоду для указанного города
        """

        # Проверка, что город введен корректно
        # if city_identifier not in self.cities:
        #     return None

        url = self.get_city_url(city_identifier)

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Проверяем, что получили HTML
            if "text/html" not in response.headers.get("Content-Type", ""):
                print(f"Ошибка: ожидался HTML, но получен {response.headers.get("Content-Type")}")
                return None

            return self.parse_weather_data(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к {url}: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None


gismeteo_parser = GismeteoParser()
