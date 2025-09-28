import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys


class BotConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Настройка бота управления ПК")
        self.root.geometry("600x500")

        # Переменные для хранения настроек
        self.token_var = tk.StringVar()
        self.allowed_users_var = tk.StringVar()

        self.load_config()
        self.create_widgets()

    def create_widgets(self):
        # Создание вкладок
        notebook = ttk.Notebook(self.root)

        # Вкладка основных настроек
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Основные настройки")

        # Токен бота
        ttk.Label(main_frame, text="Токен бота:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        token_entry = ttk.Entry(main_frame, textvariable=self.token_var, width=50)
        token_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        # Разрешенные пользователи
        ttk.Label(main_frame, text="ID разрешенных пользователей\n(через запятую):").grid(row=1, column=0, padx=10,
                                                                                          pady=10, sticky="w")
        users_entry = ttk.Entry(main_frame, textvariable=self.allowed_users_var, width=50)
        users_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить настройки", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Загрузить настройки", command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сбросить", command=self.reset_config).pack(side=tk.LEFT, padx=5)

        # Вкладка управления ботом
        manage_frame = ttk.Frame(notebook)
        notebook.add(manage_frame, text="Управление ботом")

        # Кнопки управления
        ttk.Button(manage_frame, text="Запустить бота", command=self.start_bot).pack(pady=10)
        ttk.Button(manage_frame, text="Остановить бота", command=self.stop_bot).pack(pady=10)
        ttk.Button(manage_frame, text="Проверить статус", command=self.check_status).pack(pady=10)

        # Логи
        self.log_text = scrolledtext.ScrolledText(manage_frame, height=15, width=70)
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Вкладка справки
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text="Справка")

        help_text = """
        Инструкция по настройке бота:

        1. Получите токен бота у @BotFather в Telegram
        2. Узнайте свой ID пользователя (можно получить у @userinfobot)
        3. Введите токен и ID пользователей в разделе "Основные настройки"
        4. Сохраните настройки
        5. Запустите бота в разделе "Управление ботом"

        Команды бота:
        - /start - Запуск бота
        - /help - Помощь
        - Основные команды управления ПК доступны через кнопки

        Для работы бота необходимо:
        - Установить Python 3.7+
        - Установить зависимости: pip install aiogram pyautogui psutil winapps
        - Разрешить боту доступ к системе
        """

        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def load_config(self):
        """Загрузка настроек из config.py"""
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                content = f.read()

            # Извлекаем токен
            import re
            token_match = re.search(r"API_TOKEN = '([^']+)'", content)
            if token_match:
                self.token_var.set(token_match.group(1))

            # Извлекаем список пользователей
            users_match = re.search(r"ALLOWED_USERS = \[([^\]]+)\]", content)
            if users_match:
                users_str = users_match.group(1).replace("'", "").replace('"', '')
                self.allowed_users_var.set(users_str)

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл config.py не найден!")

    def save_config(self):
        """Сохранение настроек в config.py"""
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                content = f.read()

            # Обновляем токен
            import re
            new_token = f"API_TOKEN = '{self.token_var.get()}'"
            content = re.sub(r"API_TOKEN = '[^']+'", new_token, content)

            # Обновляем список пользователей
            users_list = [uid.strip() for uid in self.allowed_users_var.get().split(',') if uid.strip()]
            users_str = "', '".join(users_list)
            new_users = f"ALLOWED_USERS = ['{users_str}']"
            content = re.sub(r"ALLOWED_USERS = \[[^\]]+\]", new_users, content)

            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(content)

            messagebox.showinfo("Успех", "Настройки сохранены!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def reset_config(self):
        """Сброс настроек к значениям по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить настройки?"):
            self.token_var.set("")
            self.allowed_users_var.set("")

    def start_bot(self):
        """Запуск бота"""
        try:
            # Проверяем настройки
            if not self.token_var.get():
                messagebox.showerror("Ошибка", "Токен бота не указан!")
                return

            if not self.allowed_users_var.get():
                messagebox.showerror("Ошибка", "Не указаны ID пользователей!")
                return

            # Сохраняем настройки перед запуском
            self.save_config()

            # Запускаем бота в отдельном процессе
            import subprocess
            if sys.platform == "win32":
                subprocess.Popen([sys.executable, "run.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, "run.py"])

            self.log_text.insert(tk.END, "Бот запущен...\n")
            self.log_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить бота: {str(e)}")

    def stop_bot(self):
        """Остановка бота"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline'] and 'run.py' in proc.info['cmdline']:
                    proc.terminate()

            self.log_text.insert(tk.END, "Бот остановлен...\n")
            self.log_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить бота: {str(e)}")

    def check_status(self):
        """Проверка статуса бота"""
        try:
            import psutil
            bot_running = False

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline'] and 'run.py' in proc.info['cmdline']:
                    bot_running = True
                    break

            if bot_running:
                self.log_text.insert(tk.END, "Статус: Бот запущен и работает\n")
            else:
                self.log_text.insert(tk.END, "Статус: Бот не запущен\n")

            self.log_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить статус: {str(e)}")


def main():
    root = tk.Tk()
    app = BotConfigApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()