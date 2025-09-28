from aiogram.utils import executor
from config import dp, bot, ALLOWED_USERS
import callbacks
import functions
import logging


async def on_startup(_):
    logging.info('Бот запущен и готов к работе!')


def start():
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        logging.info("Перезапуск через 5 секунд...")
        import time
        time.sleep(5)
        start()

if __name__ == '__main__':
    start()