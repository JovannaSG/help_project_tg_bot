from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup

from config import subscribed_users, user_cities
from services.weather import weather_service
from keyboards import exit_keyboard, main_menu_keyboard

router = Router()


class FSMChooseCity(StatesGroup):
    city_choice_state = State()


@router.message(
    F.text == "Получить прогноз погоды🌤️",
    StateFilter(default_state)
)
async def get_weather(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Введите название города",
        reply_markup=exit_keyboard
    )
    await state.set_state(FSMChooseCity.city_choice_state)


@router.message(Command("weather"), StateFilter(default_state))
async def command_get_weather(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Введите название города", 
        reply_markup=exit_keyboard
    )
    await state.set_state(FSMChooseCity.city_choice_state)


@router.message(StateFilter(FSMChooseCity.city_choice_state))
async def print_weather_forecast(
    message: types.Message,
    state: FSMContext
) -> None:
    city_name = message.text
    
    # Проверяем, находится ли пользователь в процессе подписки
    user_data = await state.get_data()
    is_subscribing = user_data.get("subscribing", False)
    
    # Получаем прогноз погоды
    weather_text = await weather_service.get_weather_forecast(city_name)
    
    if weather_text is None:
        await message.reply(
            text="Ошибка: неправильный ввод названия, повторите еще раз",
            reply_markup=exit_keyboard
        )
    else:
        if is_subscribing:
            # Если это подписка - сохраняем пользователя
            user_id = message.from_user.id
            subscribed_users.add(user_id)
            user_cities[user_id] = city_name
            
            await message.reply(
                f"✅ Вы успешно подписались на ежедневную рассылку погоды для города {city_name}!\n\n"
                f"Пример рассылки:\n{weather_text}",
                reply_markup=main_menu_keyboard
            )
            # Сбрасываем флаг подписки
            await state.update_data(subscribing=False)
        else:
            # Если просто запрос погоды
            await message.reply(weather_text, reply_markup=main_menu_keyboard)
        
        await state.set_state(default_state)
