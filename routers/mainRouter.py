from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from keyboards import main_menu_keyboard

router = Router()


# Обработчик команды /start
@router.message(Command("start", prefix="/"))
async def start_command(message: types.Message):
    await message.answer(
        "Приветствую, я бот для просмотра прогноза погоды\n\nВыберите действие:",
        reply_markup=main_menu_keyboard
    )


# перехватывать callback данные при нажатии кнопки на клавиатуре
@router.callback_query(F.data == "back_to_default_state")
async def back_to_main(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    await state.set_state(default_state)
    await callback.message.answer(
        text="Выберите действие",
        reply_markup=main_menu_keyboard
    )
    await callback.answer()
