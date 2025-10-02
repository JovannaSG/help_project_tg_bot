import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot

from config import subscribed_users, user_cities, TIMEZONE
from services.weather import weather_service

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def send_daily_weather(self, bot: Bot) -> None:
        """Отправка ежедневной рассылки погоды"""
        logger.info("Запуск ежедневной рассылки погоды...")
        
        if not subscribed_users:
            logger.info("Нет подписанных пользователей для рассылки")
            return
        
        success_count: int = 0
        error_count: int = 0
        
        # Создаем копию чтобы избежать изменения во время итерации
        users_to_process = subscribed_users.copy()
        
        for user_id in users_to_process:
            try:
                # Получаем город пользователя
                city = user_cities.get(user_id, "Иркутск")
                
                # Получаем прогноз погоды
                weather_text = await weather_service.get_weather_forecast(city)
                
                if weather_text:
                    await bot.send_message(
                        user_id, 
                        f"🌅 Доброе утро! Ваша ежедневная рассылка погоды:\n\n{weather_text}\n\n"
                        f"💡 Чтобы отписаться: /unsubscribe"
                    )
                    success_count += 1
                    logger.debug(f"✅ Погода отправлена пользователю {user_id} для города {city}")
                else:
                    # Если не удалось получить погоду для города
                    await bot.send_message(
                        user_id,
                        f"❌ Не удалось получить погоду для города {city}."
                        "Проверьте правильность названия.\n"
                        f"Используйте /subscribe чтобы изменить город."
                    )
                    error_count += 1                    
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Ошибка отправки пользователю {user_id}: {e}")
                
                # Если пользователь заблокировал бота, удаляем из подписок
                if "bot was blocked" in str(e).lower() or "Forbidden" in str(e):
                    subscribed_users.discard(user_id)
                    if user_id in user_cities:
                        del user_cities[user_id]
                    logger.info(f"🗑️ Пользователь {user_id} удален из подписок")

        logger.info(f"📊 Рассылка завершена. Успешно: {success_count}, Ошибок: {error_count}")

    def setup_schedule(self, bot: Bot):
        """Настройка расписания"""
        # Основная рассылка каждый день в 8:00
        self.scheduler.add_job(
            self.send_daily_weather,
            trigger=CronTrigger(
                hour=9,
                minute=0, 
                timezone=TIMEZONE
            ),
            args=[bot]
        )

        # Для тестирования - каждые 2 минуты
        self.scheduler.add_job(
            self.send_daily_weather,
            trigger='interval',
            minutes=2,
            args=[bot],
            id='test_schedule'
        )
    
    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()
        logger.info("Планировщик запущен")
    
    def shutdown(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик остановлен")


# Глобальный экземпляр планировщика
scheduler_service = SchedulerService()
