from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types




API_TOKEN = '7867940973:AAEpK9W9htZrpT2TkSufqDUTiNAB3qJgKHE'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)