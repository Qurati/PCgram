import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import subprocess
import psutil
import re
import winreg
import requests


class BotConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Настройка бота управления ПК")
        self.root.geometry("750x650")
        self.root.minsize(650, 550)

        # Получаем правильную рабочую директорию
        self.working_dir = self.get_working_directory()

        # Центрирование окна
        self.center_window()

        # Переменные для хранения настроек
        self.token_var = tk.StringVar()
        self.allowed_users_var = tk.StringVar()
        self.autostart_var = tk.BooleanVar()

        self.bot_process = None

        # Инициализируем log_text как None
        self.log_text = None

        # Сначала создаем виджеты, потом загружаем конфиг
        self.create_widgets()
        self.load_config()
        self.check_autostart_status()

    def get_working_directory(self):
        """Получить правильную рабочую директорию"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Создание вкладок
        notebook = ttk.Notebook(self.root)

        # Вкладка основных настроек
        main_frame = ttk.Frame(notebook, padding="10")
        notebook.add(main_frame, text="Основные настройки")

        # Токен бота
        ttk.Label(main_frame, text="Токен бота:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10,
                                                                                   sticky="w")
        token_entry = ttk.Entry(main_frame, textvariable=self.token_var, width=60, font=('Arial', 9))
        token_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        ttk.Label(main_frame, text="Получите у @BotFather в Telegram", font=('Arial', 8), foreground="gray").grid(row=1,
                                                                                                                  column=1,
                                                                                                                  sticky="w",
                                                                                                                  padx=10)

        # Кнопка проверки токена
        ttk.Button(main_frame, text="🔍 Проверить токен", command=self.check_token).grid(row=1, column=1, sticky="e",
                                                                                        padx=10)

        # Разрешенные пользователи
        ttk.Label(main_frame, text="ID разрешенных пользователей:", font=('Arial', 10, 'bold')).grid(row=2, column=0,
                                                                                                     padx=10, pady=10,
                                                                                                     sticky="nw")
        ttk.Label(main_frame, text="Через запятую, например: 123456,789012", font=('Arial', 8), foreground="gray").grid(
            row=3, column=1, sticky="w", padx=10)

        users_entry = ttk.Entry(main_frame, textvariable=self.allowed_users_var, width=60, font=('Arial', 9))
        users_entry.grid(row=2, column=1, rowspan=2, padx=10, pady=10, sticky="we")

        # Автозагрузка
        autostart_frame = ttk.Frame(main_frame)
        autostart_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky="w")

        autostart_check = ttk.Checkbutton(autostart_frame, text="Запускать бота автоматически при старте Windows",
                                          variable=self.autostart_var, command=self.toggle_autostart)
        autostart_check.pack(side=tk.LEFT, padx=10)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="💾 Сохранить настройки", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 Загрузить настройки", command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Сбросить", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔍 Проверить ID", command=self.get_user_id).pack(side=tk.LEFT, padx=5)

        # Вкладка управления ботом
        manage_frame = ttk.Frame(notebook, padding="10")
        notebook.add(manage_frame, text="Управление ботом")

        # Кнопки управления
        control_frame = ttk.Frame(manage_frame)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text="🚀 Запустить бота (скрыто)", command=self.start_bot_hidden).pack(side=tk.LEFT,
                                                                                                        padx=5)
        ttk.Button(control_frame, text="🚀 Запустить бота (видимо)", command=self.start_bot_visible).pack(side=tk.LEFT,
                                                                                                         padx=5)
        ttk.Button(control_frame, text="🛑 Остановить бота", command=self.stop_bot).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Проверить статус", command=self.check_status).pack(side=tk.LEFT, padx=5)

        # Логи
        ttk.Label(manage_frame, text="Лог выполнения:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(20, 5))

        self.log_text = scrolledtext.ScrolledText(manage_frame, height=15, width=80, font=('Consolas', 9))
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

        # Вкладка справки
        help_frame = ttk.Frame(notebook, padding="10")
        notebook.add(help_frame, text="Справка")

        help_text = f"""📋 Инструкция по настройке бота:

1. 🔐 Получите токен бота у @BotFather в Telegram
   - Напишите /newbot и следуйте инструкциям
   - Скопируйте полученный токен (формат: 1234567890:ABCDEFGhIjKlMnOpQrStUvWxYz)
   - Нажмите "Проверить токен" для проверки

2. 👤 Узнайте свой ID пользователя
   - Найдите @userinfobot в Telegram
   - Отправьте любое сообщение
   - Скопируйте ваш ID из ответа бота

3. ⚙️ Настройте параметры:
   - Введите токен в поле "Токен бота"
   - Укажите ID пользователей через запятую
   - Сохраните настройки

4. 🚀 Запустите бота:
   - Перейдите во вкладку "Управление ботом"
   - "Запустить бота (скрыто)" - бот работает в фоне без окна
   - "Запустить бота (видимо)" - открывается консольное окно для отладки

5. ⚡ Автозагрузка:
   - Отметьте "Запускать бота автоматически при старте Windows"
   - Бот будет запускаться при каждой загрузке системы

Текущая рабочая директория: {self.working_dir}

🔧 Команды бота:
- /start - Запуск бота
- /help - Помощь
- Основные команды управления ПК доступны через кнопки

⚠️ Важно!
- Убедитесь, что токен правильный (начинается с цифр, содержит двоеточие)
- Убедитесь, что установлен Python 3.7+
- Разрешите боту доступ к системе
- Не передавайте токен третьим лицам
- Регулярно обновляйте зависимости

📞 Поддержка:
Если возникли проблемы, проверьте:
1. Корректность токена
2. Правильность ID пользователя
3. Наличие интернет-соединения
4. Разрешения бота в Telegram"""

        help_label = tk.Text(help_frame, wrap=tk.WORD, font=('Arial', 9), height=25, padx=10, pady=10)
        help_label.insert(tk.END, help_text)
        help_label.config(state=tk.DISABLED)
        help_label.pack(fill=tk.BOTH, expand=True)

        notebook.pack(expand=True, fill='both')

        # Добавляем отладочную информацию
        self.log(f"Приложение запущено. Рабочая директория: {self.working_dir}")
        self.log(f"Python: {sys.executable}")

    def log(self, message):
        """Безопасное добавление сообщения в лог"""
        if self.log_text:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)

    def check_token(self):
        """Проверить валидность токена"""
        token = self.token_var.get().strip()

        if not token:
            messagebox.showwarning("Предупреждение", "Введите токен бота для проверки")
            return

        # Проверка формата токена
        if not re.match(r'^\d+:[a-zA-Z0-9_-]+$', token):
            messagebox.showerror("Ошибка",
                                 "Неверный формат токена!\n"
                                 "Токен должен быть в формате: 1234567890:ABCDEFGhIjKlMnOpQrStUvWxYz\n"
                                 "Где:\n"
                                 "- Первая часть: цифры (ID бота)\n"
                                 "- Вторая часть: буквы и цифры (секретный ключ)\n"
                                 "- Разделены двоеточием")
            return

        # Проверка токена через Telegram API
        try:
            self.log("Проверка токена через Telegram API...")
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data['result']
                    messagebox.showinfo("Успех",
                                        f"Токен действителен!\n\n"
                                        f"Бот: @{bot_info['username']}\n"
                                        f"Имя: {bot_info['first_name']}\n"
                                        f"ID: {bot_info['id']}")
                    self.log("✅ Токен прошел проверку")
                else:
                    messagebox.showerror("Ошибка", "Токен недействителен")
                    self.log("❌ Токен не прошел проверку")
            else:
                messagebox.showerror("Ошибка", f"Ошибка проверки токена: {response.status_code}")
                self.log(f"❌ Ошибка HTTP: {response.status_code}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {str(e)}")
            self.log(f"❌ Ошибка подключения: {str(e)}")

    def get_bot_exe_path(self):
        """Получить путь к исполняемому файлу бота"""
        # Сначала проверяем скомпилированную версию
        exe_path = os.path.join(self.working_dir, "PC_Controller_Bot.exe")
        if os.path.exists(exe_path):
            return exe_path

        # Если нет, проверяем Python скрипт
        script_path = os.path.join(self.working_dir, "run.py")
        if os.path.exists(script_path):
            return f'"{sys.executable}" "{script_path}"'

        self.log(f"❌ Не найден файл бота. Искали: {exe_path} и {script_path}")
        return None

    def find_bot_files(self):
        """Найти файлы бота в рабочей директории"""
        files = {
            'run.py': os.path.join(self.working_dir, 'run.py'),
            'bot_exe': os.path.join(self.working_dir, 'PC_Controller_Bot.exe'),
            'functions.py': os.path.join(self.working_dir, 'functions.py'),
            'callbacks.py': os.path.join(self.working_dir, 'callbacks.py'),
            'config.py': os.path.join(self.working_dir, 'config.py'),
            'kbs.py': os.path.join(self.working_dir, 'kbs.py')
        }

        found_files = {}
        for name, path in files.items():
            if os.path.exists(path):
                found_files[name] = path
                self.log(f"✅ Найден: {name}")
            else:
                self.log(f"❌ Не найден: {name} по пути: {path}")

        return found_files

    def add_to_autostart(self):
        """Добавить бота в автозагрузку Windows"""
        try:
            bot_path = self.get_bot_exe_path()
            if not bot_path:
                messagebox.showerror("Ошибка", "Не найден исполняемый файл бота!")
                return False

            # Открываем ключ автозагрузки
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )

            # Добавляем запись
            winreg.SetValueEx(key, "PC_Controller_Bot", 0, winreg.REG_SZ, bot_path)
            winreg.CloseKey(key)

            self.log("✅ Бот добавлен в автозагрузку Windows")
            return True

        except Exception as e:
            self.log(f"❌ Ошибка добавления в автозагрузку: {str(e)}")
            return False

    def remove_from_autostart(self):
        """Удалить бота из автозагрузки Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )

            # Удаляем запись
            try:
                winreg.DeleteValue(key, "PC_Controller_Bot")
                self.log("✅ Бот удален из автозагрузки Windows")
            except FileNotFoundError:
                self.log("ℹ️ Бот не был в автозагрузке")

            winreg.CloseKey(key)
            return True

        except Exception as e:
            self.log(f"❌ Ошибка удаления из автозагрузки: {str(e)}")
            return False

    def check_autostart_status(self):
        """Проверить статус автозагрузки"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )

            try:
                value, _ = winreg.QueryValueEx(key, "PC_Controller_Bot")
                self.autostart_var.set(True)
                self.log("ℹ️ Бот настроен на автозагрузку")
            except FileNotFoundError:
                self.autostart_var.set(False)

            winreg.CloseKey(key)

        except Exception as e:
            self.autostart_var.set(False)

    def toggle_autostart(self):
        """Включить/выключить автозагрузку"""
        if self.autostart_var.get():
            if not self.add_to_autostart():
                self.autostart_var.set(False)
        else:
            self.remove_from_autostart()

    def load_config(self):
        """Загрузка настроек из config.py"""
        try:
            config_path = os.path.join(self.working_dir, 'config.py')
            self.log(f"Пытаюсь загрузить конфиг из: {config_path}")

            if not os.path.exists(config_path):
                # Создаем базовый config.py если его нет
                self.create_default_config()
                self.log("Создан новый файл config.py")

            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Извлекаем токен
            token_match = re.search(r"API_TOKEN\s*=\s*'([^']+)'", content)
            if token_match:
                self.token_var.set(token_match.group(1))
                self.log("Токен загружен")
            else:
                self.log("Токен не найден в config.py")

            # Извлекаем список пользователей
            users_match = re.search(r"ALLOWED_USERS\s*=\s*\[([^\]]+)\]", content)
            if users_match:
                users_str = users_match.group(1).replace("'", "").replace('"', '').replace(" ", "")
                self.allowed_users_var.set(users_str)
                self.log("Список пользователей загружен")
            else:
                self.log("Список пользователей не найден")

        except Exception as e:
            error_msg = f"Не удалось загрузить настройки: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.log(f"Ошибка загрузки: {str(e)}")

    def create_default_config(self):
        """Создание базового config.py"""
        default_config = '''from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Список разрешенных пользователей
ALLOWED_USERS = ['YOUR_USER_ID_HERE']
'''
        config_path = os.path.join(self.working_dir, 'config.py')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)

    def save_config(self):
        """Сохранение настроек в config.py"""
        try:
            token = self.token_var.get().strip()
            users_str = self.allowed_users_var.get().strip()

            if not token:
                messagebox.showerror("Ошибка", "Токен бота не может быть пустым!")
                return

            # Проверка формата токена перед сохранением
            if not re.match(r'^\d+:[a-zA-Z0-9_-]+$', token):
                messagebox.showerror("Ошибка",
                                     "Неверный формат токена!\n\n"
                                     "Токен должен быть в формате:\n"
                                     "1234567890:ABCDEFGhIjKlMnOpQrStUvWxYz\n\n"
                                     "Получите правильный токен у @BotFather")
                return

            if not users_str:
                messagebox.showerror("Ошибка", "Не указаны ID пользователей!")
                return

            # Проверяем формат ID пользователей
            users_list = [uid.strip() for uid in users_str.split(',') if uid.strip()]
            for uid in users_list:
                if not uid.isdigit():
                    messagebox.showerror("Ошибка",
                                         f"Некорректный ID пользователя: {uid}\nID должен содержать только цифры")
                    return

            config_path = os.path.join(self.working_dir, 'config.py')
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Обновляем токен
            new_token = f"API_TOKEN = '{token}'"
            content = re.sub(r"API_TOKEN\s*=\s*'[^']*'", new_token, content)

            # Обновляем список пользователей
            users_str = "', '".join(users_list)
            new_users = f"ALLOWED_USERS = ['{users_str}']"
            content = re.sub(r"ALLOWED_USERS\s*=\s*\[[^\]]*\]", new_users, content)

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            messagebox.showinfo("Успех", "Настройки сохранены!")
            self.log("Настройки успешно сохранены")

        except Exception as e:
            error_msg = f"Не удалось сохранить настройки: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.log(f"Ошибка сохранения: {str(e)}")

    def reset_config(self):
        """Сброс настроек к значениям по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить настройки?"):
            self.token_var.set("")
            self.allowed_users_var.set("")
            self.log("Настройки сброшены")

    def get_user_id(self):
        """Открыть инструкцию по получению ID"""
        messagebox.showinfo("Получение ID пользователя",
                            "Чтобы получить ваш ID пользователя:\n\n"
                            "1. Найдите @userinfobot в Telegram\n"
                            "2. Отправьте любое сообщение\n"
                            "3. Скопируйте ваш ID из ответа бота\n\n"
                            "ID должен содержать только цифры!")

    def start_bot_hidden(self):
        """Запуск бота без отображения окна"""
        self.start_bot(hidden=True)

    def start_bot_visible(self):
        """Запуск бота с отображением окна (для отладки)"""
        self.start_bot(hidden=False)

    def start_bot(self, hidden=True):
        """Запуск бота"""
        try:
            # Проверяем настройки
            token = self.token_var.get().strip()
            if not token or token == 'YOUR_BOT_TOKEN_HERE':
                messagebox.showerror("Ошибка", "Сначала укажите токен бота в настройках!")
                return

            # Проверяем формат токена перед запуском
            if not re.match(r'^\d+:[a-zA-Z0-9_-]+$', token):
                messagebox.showerror("Ошибка",
                                     "Неверный формат токена!\n\n"
                                     "Перед запуском бота:\n"
                                     "1. Получите токен у @BotFather\n"
                                     "2. Проверьте формат токена\n"
                                     "3. Нажмите 'Проверить токен'")
                return

            if not self.allowed_users_var.get() or self.allowed_users_var.get() == 'YOUR_USER_ID_HERE':
                messagebox.showerror("Ошибка", "Сначала укажите ID пользователей в настройках!")
                return

            # Сохраняем настройки перед запуском
            self.save_config()

            # Проверяем доступные файлы бота
            bot_files = self.find_bot_files()

            # Определяем что запускать
            bot_exe_path = os.path.join(self.working_dir, "PC_Controller_Bot.exe")
            bot_script_path = os.path.join(self.working_dir, "run.py")

            command = None
            if os.path.exists(bot_exe_path):
                # Запускаем скомпилированный EXE
                command = [bot_exe_path]
                self.log("Запуск скомпилированного бота (EXE)")
            elif os.path.exists(bot_script_path):
                # Запускаем Python скрипт
                command = [sys.executable, bot_script_path]
                self.log("Запуск бота через Python скрипт")
            else:
                messagebox.showerror("Ошибка",
                                     f"Не найден файл бота!\n"
                                     f"Искал здесь:\n"
                                     f"EXE: {bot_exe_path}\n"
                                     f"Python: {bot_script_path}\n\n"
                                     f"Убедитесь, что все файлы находятся в одной папке.")
                return

            # Останавливаем предыдущий процесс, если он запущен
            if self.bot_process and self.bot_process.poll() is None:
                self.bot_process.terminate()
                self.log("Предыдущий процесс бота остановлен")

            # Запускаем бота в отдельном процессе
            self.log(f"Запуск бота... ({'скрытый режим' if hidden else 'видимый режим'})")

            if hidden:
                # Скрытый запуск (без окна консоли)
                if sys.platform == "win32":
                    # Для Windows используем CREATE_NO_WINDOW
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = 0  # SW_HIDE

                    self.bot_process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        cwd=self.working_dir
                    )
                else:
                    # Для Linux/Mac
                    self.bot_process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=self.working_dir
                    )

                # Проверяем через 3 секунды, жив ли процесс
                self.root.after(3000, self.check_bot_health)

            else:
                # Видимый запуск (с окном консоли)
                if sys.platform == "win32":
                    # Для видимого запуска используем обычный Popen без специальных флагов
                    # Это создаст консольное окно
                    self.bot_process = subprocess.Popen(
                        command,
                        cwd=self.working_dir
                    )
                else:
                    # Для Linux/Mac
                    self.bot_process = subprocess.Popen(
                        command,
                        cwd=self.working_dir
                    )

                self.log(f"Бот запущен в видимом режиме. Должно появиться консольное окно.")

            self.log(f"Бот запущен с PID: {self.bot_process.pid}")
            self.log(f"Команда: {' '.join(command)}")
            self.log(f"Рабочая директория: {self.working_dir}")

        except Exception as e:
            error_msg = f"Не удалось запустить бота: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.log(f"Ошибка запуска: {str(e)}")

    def check_bot_health(self):
        """Проверить, не завершился ли бот из-за ошибки"""
        if self.bot_process and self.bot_process.poll() is not None:
            # Процесс завершился - читаем stderr
            try:
                stderr_output = self.bot_process.stderr.read()
                if stderr_output:
                    self.log(f"❌ Бот завершился с ошибкой:\n{stderr_output}")
                    messagebox.showerror("Ошибка бота",
                                         f"Бот завершился с ошибкой:\n\n{stderr_output[:500]}...\n\n"
                                         f"Проверьте:\n"
                                         f"1. Корректность токена\n"
                                         f"2. Наличие интернета\n"
                                         f"3. Разрешения бота")
                else:
                    self.log("❌ Бот завершился без вывода ошибки")
            except:
                self.log("❌ Бот завершился, но не удалось прочитать ошибку")
        else:
            # Процесс еще работает
            self.log("✅ Бот успешно запущен и работает")

    def stop_bot(self):
        """Остановка бота"""
        try:
            bot_stopped = False

            # Останавливаем наш процесс, если он запущен
            if self.bot_process and self.bot_process.poll() is None:
                self.bot_process.terminate()
                self.log(f"Бот остановлен (PID: {self.bot_process.pid})")
                bot_stopped = True
                self.bot_process = None

            # Дополнительно ищем и останавливаем другие процессы бота
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'run.py' in cmdline or 'PC_Controller_Bot.exe' in cmdline:
                        if proc.info['pid'] != os.getpid():  # Не останавливаем себя
                            proc.terminate()
                            self.log(f"Дополнительный процесс бота остановлен (PID: {proc.info['pid']})")
                            bot_stopped = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            if not bot_stopped:
                self.log("Бот не был запущен")

        except Exception as e:
            error_msg = f"Не удалось остановить бота: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.log(f"Ошибка остановки: {str(e)}")

    def check_status(self):
        """Проверка статуса бота"""
        try:
            bot_running = False

            # Проверяем наш процесс
            if self.bot_process and self.bot_process.poll() is None:
                bot_running = True
                self.log(f"✅ Статус: Бот запущен (PID: {self.bot_process.pid})")
            else:
                # Ищем другие процессы бота
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'run.py' in cmdline or 'PC_Controller_Bot.exe' in cmdline:
                            if proc.info['pid'] != os.getpid():  # Не показываем себя
                                bot_running = True
                                self.log(f"✅ Статус: Бот запущен (PID: {proc.info['pid']})")
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

            if not bot_running:
                self.log("❌ Статус: Бот не запущен")

        except Exception as e:
            error_msg = f"Не удалось проверить статус: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.log(f"Ошибка проверки статуса: {str(e)}")


def main():
    root = tk.Tk()
    app = BotConfigApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()