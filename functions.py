import pyautogui
import os
import webbrowser
from config import *

@dp.message_handler()
async def func(message: types.Message):
    if str(message.from_user.id) in ['6578319405', '1283072914']:
        if message.text == 'Скрин':
            screenshot = pyautogui.screenshot()
            # Сохраняем скриншот во временный файл
            screenshot_file = "screenshot.png"
            screenshot.save(screenshot_file)

            # Отправляем файл пользователю
            with open(screenshot_file, 'rb') as file:
                await message.reply_photo(photo=file)

            # Удаляем временный файл
            os.remove(screenshot_file)
        elif message.text[:4] == 'http':
            webbrowser.open(message.text)
        elif message.text == 'off':
            os.system("shutdown now")
        elif message.text.split(' ')[0] == 'Открой':
            os.startfile(f"{message.text.split(' ', 1)[1]}.exe")