from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

API_TOKEN = ''
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Список разрешенных пользователей
ALLOWED_USERS = ['6578319405', '1283072914']