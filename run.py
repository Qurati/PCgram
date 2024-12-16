from aiogram.utils import executor
from config import *
from functions import *




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)