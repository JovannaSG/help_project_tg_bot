from datetime import datetime
from typing import Any, Optional


class WeatherAnalyzer:
    def __init__(self) -> None:
        # Веса источников, какому из них больше доверяем
        # Значения [0, 1]
        self.source_weights: dict[str, float] = {
            "source1": 0.5,
            "source2": 0.5
        }
        # Пределы допустимых отклонений для валидации
        self.validation_thresholds: dict[str, float] = {
            "temperature": 5.0,  # +- 5 градусов
            "humidity": 30,      # +- 30%
            "pressure": 50,      # +- 50 гПа
            "wind": 10,          # +- 10 м/c
        }
        # Для проверки соответствия описания погоды
        self.weather_description_map: dict[str, list[str]] = {
            "Mist": ["туман", "дымка", "облачно", "пасмурно"],
            "Clear": ["ясно", "безоблачно", "солнечно"],
            "Clouds": ["облачно", "малооблачно", "переменная облачность"],
            "Rain": ["дождь", "ливень", "морось"],
            "Snow": ["снег", "снегопад", "метель"]
        }

    def _check_outliers(
        self,
        data1: dict[str, Any],
        data2: dict[str, Any]
    ) -> list[str]:
        """
        Проверка на аномальные значения
        """

        warnings: list[str] = []

        # Проверка температуры
        if "temperature" in data1 and "temperature" in data2:
            temp_diff = abs(data1["temperature"] - data2["temperature"])
            if temp_diff > self.validation_thresholds["temperature"]:
                warnings.append(f"Большое расхождение в температуре: {temp_diff:.1f}°C")

        # Проверка влажности
        if "humidity" in data1 and "humidity" in data2:
            humid_diff = abs(data1["humidity"] - int(data2["humidity"]))
            if humid_diff > self.validation_thresholds["humidity"]:
                warnings.append(f"Большое расхождение во влажности: {humid_diff}%")

        # Проверка давления
        if "pressure" in data1 and "pressure" in data2:
            press_diff = abs(data1["pressure"] - int(data2["pressure"]))
            if press_diff > self.validation_thresholds["pressure"]:
                warnings.append(f"Большое расхождение в давлении: {press_diff} гПа")

        return warnings

    def _weighted_average(
        self,
        value1: Optional[float],
        value2: Optional[float],
        weight1: float,
        weight2: float
    ) -> Optional[float]:
        """
        Взвешенное среднее значение
        """

        if value1 is None and value2 is None:
            return None
        elif value1 is None:
            return value2
        elif value2 is None:
            return value1
        else:
            return (value1 * weight1 + value2 * weight2) / (weight1 + weight2)

    def merge_temperature_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение данных о температуре
        """

        temp_data: dict = {}

        # Основная температура
        temp1 = data1.get("temperature")
        temp2 = data2.get("temperature")

        if temp1 is not None and temp2 is not None:
            # Преобразуем temp2 в float, если это строка
            temp2_value = float(temp2) if isinstance(temp2, str) else temp2
            merged_temp = self._weighted_average(
                temp1, temp2_value,
                self.source_weights["source1"],
                self.source_weights["source2"]
            )
            temp_data["temperature"] = round(merged_temp, 1)
            temp_data["temperature_source"] = "combined"
        elif temp1 is not None:
            temp_data["temperature"] = round(temp1, 1)
            temp_data["temperature_source"] = "source1"
        elif temp2 is not None:
            temp2_value = float(temp2) if isinstance(temp2, str) else temp2
            temp_data["temperature"] = round(float(temp2_value), 1)
            temp_data["temperature_source"] = "source2"

        # Температура по ощущениям
        feels_temp = data1.get("feels_like") or data2.get("feels_like")
        if feels_temp is not None:
            temp_data["feels_like"] = round(float(feels_temp), 1)

        return temp_data

    def merge_humidity_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение данных о влажности
        """

        humidity_data: dict = {}

        humid1 = data1.get("humidity")
        humid2 = data2.get("humidity")

        if humid1 is not None and humid2 is not None:
            # Преобразуем humid2 в int, если это строка
            humid2_value = int(humid2) if isinstance(humid2, str) else humid2
            merged_humid = self._weighted_average(
                float(humid1), float(humid2_value),
                self.source_weights["source1"],
                self.source_weights["source2"]
            )
            humidity_data["humidity"] = int(merged_humid)
            humidity_data["humidity_source"] = "combined"
        elif humid1 is not None:
            humidity_data["humidity"] = int(humid1)
            humidity_data["humidity_source"] = "source1"
        elif humid2 is not None:
            humid2_value = int(humid2) if isinstance(humid2, str) else humid2
            humidity_data["humidity"] = int(humid2_value)
            humidity_data["humidity_source"] = "source2"

        return humidity_data

    def merge_pressure_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение данных о давлении
        """

        pressure_data: dict = {}

        press1 = data1.get("pressure")
        press2 = data2.get("pressure")

        if press1 is not None and press2 is not None:
            # Преобразуем press2 в int, если это строка
            press2_value = int(press2) if isinstance(press2, str) else press2
            merged_press = self._weighted_average(
                press1, press2_value,
                self.source_weights["source1"],
                self.source_weights["source2"]
            )
            pressure_data["pressure_hpa"] = round(merged_press)
            pressure_data["pressure_mmhg"] = round(merged_press / 1.333)
            pressure_data["pressure_source"] = "combined"
        elif press1 is not None:
            pressure_data["pressure_hpa"] = press1
            pressure_data["pressure_mmhg"] = round(press1 / 1.333)
            pressure_data["pressure_source"] = "source1"
        elif press2 is not None:
            press2_value = int(press2) if isinstance(press2, str) else press2
            pressure_data["pressure_hpa"] = round(press2_value * 1.333)
            pressure_data["pressure_mmhg"] = press2_value
            pressure_data["pressure_source"] = "source2"

        return pressure_data

    def merge_wind_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение данных о ветре
        """

        wind_data: dict = {}

        wind1 = data1.get("wind")
        wind2 = data2.get("wind")

        if wind1 is not '' and wind2 is not '':
            wind2_float = float(wind2) if isinstance(wind2, (int, float, str)) else 0.0
            merged_wind = self._weighted_average(
                wind1, wind2_float,
                self.source_weights["source1"],
                self.source_weights["source2"]
            )
            wind_data["wind_speed"] = round(merged_wind, 1)
            wind_data["wind_description"] = self._get_wind_description(merged_wind)
            wind_data["wind_source"] = "combined"
        elif wind1 is not None:
            wind_data["wind_speed"] = wind1
            wind_data["wind_description"] = self._get_wind_description(wind1)
            wind_data["wind_source"] = "source1"
        elif wind2 is not None:
            wind2_float = float(wind2) if isinstance(wind2, (int, float, str)) else 0.0
            wind_data["wind_speed"] = round(wind2_float, 1)
            wind_data["wind_description"] = self._get_wind_description(wind2_float)
            wind_data["wind_source"] = "source2"

        # Направление ветра, если есть
        wind_dir = data1.get("wind_direction") or data2.get("wind_direction")
        if wind_dir:
            wind_data["wind_direction"] = wind_dir

        return wind_data

    def _get_wind_description(self, speed: float) -> str:
        """
        Получить текстовое описание силы ветра
        """

        if speed < 0.5:
            return "штиль"
        elif speed < 1.5:
            return "слабый ветер"
        elif speed < 5.0:
            return "легкий ветер"
        elif speed < 10.0:
            return "умеренный ветер"
        elif speed < 15.0:
            return "сильный ветер"
        else:
            return "очень сильный ветер"

    def merge_weather_description(self, data1: dict, data2: dict) -> dict:
        """
        Объединение описаний погоды
        """

        desc_data: dict = {}

        desc1 = data1.get("weather_description")
        desc2 = data2.get("description") or data2.get("weather_description")

        if desc1 and desc2:
            desc_data["weather_description"] = f"{desc2} ({desc1})"
            desc_data["description_source"] = "combined"
        elif desc1:
            desc_data["weather_description"] = desc1
            desc_data["description_source"] = "source1"
        elif desc2:
            desc_data["weather_description"] = desc2
            desc_data["description_source"] = "source2"

        return desc_data

    def merge_sun_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение данных о солнце
        """

        sun_data: dict = {}

        # Проверяем оба источника
        sunrise1 = data1.get("sunrise_timestamp")
        sunset1 = data1.get("sunset_timestamp")
        sunrise2 = data2.get("sunrise_timestamp")
        sunset2 = data2.get("sunset_timestamp")

        if sunrise1 and sunset1:
            sun_data["sunrise"] = sunrise1.strftime("%H:%M") if isinstance(sunrise1, datetime) else sunrise1
            sun_data["sunset"] = sunset1.strftime("%H:%M") if isinstance(sunset1, datetime) else sunset1
            sun_data["sun_data_source"] = "source1"
        elif sunrise2 and sunset2:
            sun_data["sunrise"] = sunrise2.strftime("%H:%M") if isinstance(sunrise2, datetime) else sunrise2
            sun_data["sunset"] = sunset2.strftime("%H:%M") if isinstance(sunset2, datetime) else sunset2
            sun_data["sun_data_source"] = "source2"

        # Длина дня
        day_length = data1.get("length_of_the_day") or data2.get("length_of_the_day")
        if day_length:
            sun_data["day_length"] = str(day_length)

        return sun_data

    def merge_location_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение данных о местоположении
        """

        location_data: dict = {}

        # Город
        city = data1.get("city") or data2.get("city") or "Неизвестный город"
        location_data["city"] = city

        # Координаты
        lat = data1.get("latitude") or data2.get("latitude")
        lon = data1.get("longitude") or data2.get("longitude")
        if lat and lon:
            location_data["latitude"] = lat
            location_data["longitude"] = lon

        return location_data

    def calculate_confidence_score(self, data1: dict, data2: dict) -> float:
        """
        Расчет уровня доверия к объединенным данным
        """

        score: float = 0.5
        matching_fields: int = 0
        total_fields: int = 0

        fields_to_check = ["temperature", "wind", "humidity", "pressure"]

        for field in fields_to_check:
            val1 = data1.get(field)
            val2 = data2.get(field)
            if val1 is not None and val2 is not None:
                total_fields += 1
                try:
                    # Преобразуем значения к числам
                    val1_num = float(val1) if isinstance(val1, (int, float, str)) else None
                    val2_num = float(val2) if isinstance(val2, (int, float, str)) else None
                    if val1_num is not None and val2_num is not None:
                        diff = abs(val1_num - val2_num)
                        # Пороги для разных полей
                        thresholds = {
                            "temperature": 2.0,
                            "wind": 3.0,
                            "humidity": 15,
                            "pressure": 20
                        }
                        if diff <= thresholds.get(field, 5.0):
                            matching_fields += 1
                except (ValueError, TypeError):
                    pass
        if total_fields > 0:
            match_ratio = matching_fields / total_fields
            score = 0.3 + 0.7 * match_ratio

        return round(score, 2)

    def _determine_overall_condition(self, data: dict) -> str:
        """
        Определение общего состояния погоды
        """

        temp = data.get("temperature")
        wind = data.get("wind_speed", 0)
        description = data.get("weather_description", "").lower()

        if temp is None:
            return "недостаточно данных"

        conditions = []

        # Температурные условия
        if temp < -30:
            conditions.append("экстремально холодно")
        elif temp < -20:
            conditions.append("очень холодно")
        elif temp < -10:
            conditions.append("холодно")
        elif temp < 0:
            conditions.append("морозно")
        elif temp < 10:
            conditions.append("прохладно")
        elif temp < 20:
            conditions.append("тепло")
        elif temp < 30:
            conditions.append("жарко")
        else:
            conditions.append("очень жарко")

        # Ветровые условия
        if wind > 10:
            conditions.append("ветрено")
        elif wind > 5:
            conditions.append("с ветром")

        # Атмосферные явления
        if any(word in description for word in ["туман", "mist", "дымка"]):
            conditions.append("туманно")
        if any(word in description for word in ["дождь", "rain", "ливень"]):
            conditions.append("дождливо")
        if any(word in description for word in ["снег", "snow", "метель"]):
            conditions.append("снежно")

        return ", ".join(conditions) if conditions else "нормальные условия"

    def _generate_recommendations(self, data: dict) -> dict:
        """
        Генерация рекомендаций на основе погоды
        """

        recommendations: dict = {}
        temp = data.get("temperature")
        wind = data.get("wind_speed", 0)
        description = data.get("weather_description", "").lower()

        if temp is not None:
            # Одежда
            if temp < -20:
                recommendations["clothing"] = "Теплая зимняя одежда, термобелье, шапка, шарф, варежки"
            elif temp < -10:
                recommendations["clothing"] = "Теплая куртка, шапка, перчатки"
            elif temp < 0:
                recommendations["clothing"] = "Зимняя куртка, шапка"
            elif temp < 10:
                recommendations["clothing"] = "Демисезонная куртка, свитер"
            elif temp < 20:
                recommendations["clothing"] = "Легкая куртка или ветровка"
            else:
                recommendations["clothing"] = "Легкая одежда"

            # Мероприятия
            if temp < -15:
                recommendations["activities"] = "Оставайтесь в помещении, ограничьте пребывание на улице"
            elif temp < -5:
                recommendations["activities"] = "Непродолжительные прогулки, зимние виды спорта"
            elif temp < 15:
                recommendations["activities"] = "Прогулки, активный отдых на свежем воздухе"
            else:
                recommendations["activities"] = "Идеально для прогулок и отдыха на природе"

        # Дополнительные рекомендации
        if wind > 10:
            recommendations["wind_warning"] = "Будьте осторожны на открытых пространствах"

        if any(word in description for word in ["дождь", "rain", "ливень"]):
            recommendations["umbrella"] = "Рекомендуется взять зонт"

        if "geomagnetic_activity" in data and data["geomagnetic_activity"] > 4:
            recommendations["health_warning"] = "Магнитная буря - будьте внимательны к самочувствию"

        return recommendations

    def merge_all_data(self, data1: dict, data2: dict) -> dict:
        """
        Объединение всех данных из двух источников
        """

        print(data1)
        print(data2)

        merged_data: dict = {}

        merged_data["city_name"] = data1.get("city_name", "Иркутск")

        # Проверяем выбросы
        warnings = self._check_outliers(data1, data2)
        if warnings:
            merged_data["warnings"] = warnings

        # Объединяем данные
        merged_data.update(self.merge_location_data(data1, data2))
        merged_data.update(self.merge_temperature_data(data1, data2))
        merged_data.update(self.merge_humidity_data(data1, data2))
        merged_data.update(self.merge_pressure_data(data1, data2))
        merged_data.update(self.merge_wind_data(data1, data2))
        merged_data.update(self.merge_weather_description(data1, data2))
        merged_data.update(self.merge_sun_data(data1, data2))

        # Дополнительные данные
        if "water_temperature" in data1 or "water_temperature" in data2:
            water_temp = data1.get("water_temperature") or data2.get("water_temperature")
            if water_temp:
                merged_data["water_temperature"] = round(float(water_temp), 1)

        if (
            ("geomagnetic_activity" in data1 or "geomagnetic_activity" in data2) and
            (data1.get("geomagnetic_activity") is not None and data2.get("geomagnetic_activity") is not None)
        ):
            geomag = data1.get("geomagnetic_activity") or data2.get("geomagnetic_activity")
            if geomag:
                merged_data["geomagnetic_activity"] = geomag
                # Простое описание для геомагнитной активности
                if geomag <= 3:
                    merged_data["geomagnetic_description"] = "спокойная"
                elif geomag <= 5:
                    merged_data["geomagnetic_description"] = "небольшая"
                elif geomag <= 7:
                    merged_data["geomagnetic_description"] = "умеренная"
                else:
                    merged_data["geomagnetic_description"] = "сильная"

        # Ближайший прогноз
        if "next_hours" in data1:
            merged_data["next_hours"] = data1["next_hours"]
        elif "next_hours" in data2:
            merged_data["next_hours"] = data2["next_hours"]

        # Рассчитываем уровень доверия
        merged_data["confidence_score"] = self.calculate_confidence_score(data1, data2)

        # Определяем общее состояние
        merged_data["overall_condition"] = self._determine_overall_condition(merged_data)

        # Генерируем рекомендации
        merged_data["recommendations"] = self._generate_recommendations(merged_data)

        # Источники данных
        merged_data["data_sources"] = 2

        return merged_data

    def print_weather_report(self, merged_data: dict) -> str:
        """
        Красивый вывод отчета о погоде
        """
        print(merged_data)

        result_str: str = ""

        result_str += f"ПОГОДНЫЙ ОТЧЕТ: {merged_data.get('city_name', 'Неизвестный город')}\n"

        result_str += f"\n📊 ОБЩАЯ ИНФОРМАЦИЯ:\n"
        result_str += f"   • Состояние: {merged_data.get('overall_condition', 'нет данных')}\n"
        result_str += f"   • Уровень доверия: {merged_data.get('confidence_score', 0) * 100:.0f}%\n"
        result_str += f"   • Источников данных: {merged_data.get('data_sources', 0)}\n"

        result_str += f"\n🌡 ТЕМПЕРАТУРА:\n"
        temp = merged_data.get("temperature")
        if temp:
            result_str += f"   • Воздух: {temp}°C\n"

        feels_like = merged_data.get("feels_like")
        if feels_like:
            result_str += f"   • По ощущению: {feels_like}°C\n"

        water_temp = merged_data.get("water_temperature")
        if water_temp:
            result_str += f"   • Вода: {water_temp}°C\n"

        result_str += f"\n💨 ВЕТЕР И ВЛАЖНОСТЬ:\n"
        if "wind_speed" in merged_data:
            result_str += f"   • Скорость: {merged_data.get('wind_speed', 0)} м/с ({merged_data.get('wind_description', 'нет данных')})\n"

        if "humidity" in merged_data:
            result_str += f"   • Влажность: {merged_data.get('humidity')}%\n"

        result_str += f"\n📈 АТМОСФЕРНОЕ ДАВЛЕНИЕ:\n"
        if "pressure_hpa" in merged_data:
            result_str += f"   • {merged_data.get('pressure_hpa')} гПа ({merged_data.get('pressure_mmhg', '?')} мм рт.ст.)\n"

        result_str += f"\n☀ СОЛНЕЧНЫЕ ЧАСЫ:\n"
        if "sunrise" in merged_data:
            result_str += f"   • Восход: {merged_data.get('sunrise')}\n"
            result_str += f"   • Закат: {merged_data.get('sunset')}\n"
            if "day_length" in merged_data:
                result_str += f"   • Продолжительность дня: {merged_data.get('day_length')}\n"

        if "geomagnetic_activity" in merged_data:
            result_str += f"\n⚡ ГЕОМАГНИТНАЯ АКТИВНОСТЬ:\n"
            result_str += f"   • Уровень: {merged_data.get('geomagnetic_activity')}/9 баллов\n"
            result_str += f"   • Описание: {merged_data.get('geomagnetic_description', 'нет данных')}\n"

        if "next_hours" in merged_data:
            result_str += f"\n⏰ БЛИЖАЙШИЙ ПРОГНОЗ:\n"
            next_hours = merged_data["next_hours"]
            if isinstance(next_hours, list):
                result_str += f"   • Часы: {', '.join(str(h) for h in next_hours[:5])}\n"
            else:
                result_str += f"   • Прогноз: {next_hours}\n"

        if "warnings" in merged_data and merged_data["warnings"]:
            result_str += f"\n⚠ ПРЕДУПРЕЖДЕНИЯ:\n"
            for warning in merged_data["warnings"]:
                result_str += f"   • {warning}\n"

        result_str += f"\n🎯 РЕКОМЕНДАЦИИ:\n"
        recommendations = merged_data.get("recommendations", {})
        if recommendations:
            for key, value in recommendations.items():
                result_str += f"   • {key.replace('_', ' ').title()}: {value}\n"
        else:
            result_str += "   • Нет специальных рекомендаций\n"

        return result_str


weather_analyzer = WeatherAnalyzer()
