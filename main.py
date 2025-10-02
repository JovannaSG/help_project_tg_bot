import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import config
from services.scheduler import scheduler_service
from routers.mainRouter import router as main_router
from routers.weatherRouters import router as weather_router
from routers.subscribeRouter import router as subscribe_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def set_main_menu(bot: Bot) -> None:
    main_menu_commands: list[BotCommand] = [
        BotCommand(
            command="/help",
            description="Справка о работе бота"
        ),
        BotCommand(
            command="/weather",
            description="Получить прогноз погоды"
        ),
        BotCommand(
            command="/subscribe",
            description="Подписаться на ежедневную рассылку прогноза погоды"
        ),
        BotCommand(
            command="/unsubscribe",
            description="Отписаться от ежедневной рассылки бота"
        )
    ]

    await bot.set_my_commands(main_menu_commands)


async def main():
    logger.info("Запуск бота погоды...")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    
    # Настройка роутеров
    dp.include_router(main_router)
    dp.include_router(weather_router)
    dp.include_router(subscribe_router)
    
    # Настройка и запуск планировщика
    scheduler_service.setup_schedule(bot)
    scheduler_service.start()

    try:
        # Запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        dp.startup.register(set_main_menu)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        # Корректное завершение
        scheduler_service.shutdown()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
