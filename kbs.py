from aiogram.types import ReplyKeyboardMarkup

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
buttons = ["Инфо", "Скрин", "Приложения", "Открой сайт", "Закрой окно", "Блокировка", "Сон", "Перезагрузка", "Быстрые команды", "Дополнительно"]
keyboard.add(*buttons)

quick_actions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
quick_buttons = ["Громкость +", "Громкость -", "Пауза", "Продолжить", "Диспетчер задач", "Проводник", "Свернуть все", "Обновить", "Назад"]
quick_actions_keyboard.add(*quick_buttons)

extra_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
extra_buttons = ["Процессы", "Диски", "Сеть", "Батарея", "Разрешение", "Назад"]
extra_keyboard.add(*extra_buttons)