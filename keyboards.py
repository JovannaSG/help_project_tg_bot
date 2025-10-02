from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# Создаем кнопки для главного меню
button_get_weather_forecast = KeyboardButton(text="Получить прогноз погоды🌤️")

# Создаем клавиатуру главного меню
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [button_get_weather_forecast]
    ],
    resize_keyboard=True
)

# Создаем кнопки для меню выхода
buttons: list[list[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Вернуться назад",
            callback_data="back_to_default_state"
        )
    ]
]

# Создаем клавиатуру выхода
exit_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
