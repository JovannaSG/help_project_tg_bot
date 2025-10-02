from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import subscribed_users, user_cities
from routers.weatherRouters import FSMChooseCity

router = Router()


@router.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    
    if user_id in subscribed_users:
        await message.answer("ℹ️ Вы уже подписаны на рассылку.")
        return
    
    await message.answer(
        "📝 Для подписки на ежедневную рассылку введите название вашего города:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # Сохраняем состояние что пользователь в процессе подписки
    await state.set_state(FSMChooseCity.city_choice_state)
    
    # Временное хранилище для подписки
    await state.update_data(subscribing=True)


@router.message(Command("unsubscribe"))  
async def cmd_unsubscribe(message: types.Message) -> None:
    user_id = message.from_user.id
    
    if user_id in subscribed_users:
        subscribed_users.discard(user_id)
        if user_id in user_cities:
            del user_cities[user_id]
        await message.answer("❌ Вы отписались от рассылки погоды.")
    else:
        await message.answer("ℹ️ Вы не были подписаны на рассылку.")
