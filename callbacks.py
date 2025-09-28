from aiogram import types
from config import dp
from kbs import keyboard, quick_actions_keyboard, extra_keyboard
import functions

@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply('Бот для управления ПК', reply_markup=keyboard)

@dp.message_handler(commands="help")
async def help_command(message: types.Message):
    help_text = "Команды: Инфо, Скрин, Приложения, Открой сайт, Закрой окно, Блокировка, Сон, Перезагрузка"
    await message.reply(help_text)

@dp.message_handler(lambda message: message.text == "Назад")
async def back_to_main(message: types.Message):
    await message.reply("Главное меню:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Быстрые команды")
async def quick_actions(message: types.Message):
    await message.reply("Быстрые команды:", reply_markup=quick_actions_keyboard)

@dp.message_handler(lambda message: message.text == "Дополнительно")
async def extra_features(message: types.Message):
    await message.reply("Дополнительные функции:", reply_markup=extra_keyboard)

@dp.message_handler(lambda message: message.text in ["Громкость +", "Громкость -", "Пауза", "Продолжить", "Диспетчер задач", "Проводник", "Свернуть все", "Обновить"])
async def quick_commands(message: types.Message):
    await functions.handle_quick_command(message)

@dp.message_handler(lambda message: message.text in ["Процессы", "Диски", "Сеть", "Батарея", "Разрешение"])
async def extra_commands(message: types.Message):
    await functions.handle_extra_command(message)

@dp.message_handler()
async def all_messages(message: types.Message):
    await functions.handle_message(message)