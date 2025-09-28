import os
import subprocess
import shutil
import sys


def run_command(command):
    """Выполнить команду в командной строке"""
    try:
        print(f"Выполняется: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=os.getcwd())
        print(f"Успешно: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении: {command}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False


def check_files():
    """Проверка наличия необходимых файлов"""
    required_files = [
        'run.py',
        'functions.py',
        'callbacks.py',
        'config.py',
        'kbs.py',
        'config_app.py',
        'requirements.txt'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("Отсутствуют следующие файлы:")
        for file in missing_files:
            print(f"  - {file}")
        return False

    print("Все необходимые файлы найдены!")
    return True


def build_installer():
    print("=== Сборка установщика PC Controller Bot ===")

    # Проверяем файлы
    if not check_files():
        print("Пожалуйста, убедитесь что все файлы находятся в текущей директории")
        return

    # Очищаем предыдущие сборки
    print("1. Очистка предыдущих сборок...")
    for folder in ["dist", "build", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # Удаляем старые spec файлы
    for file in os.listdir("."):
        if file.endswith(".spec"):
            os.remove(file)

    # Создаем необходимые файлы
    print("2. Создание необходимых файлов...")

    # Файл лицензии (если не существует)
    if not os.path.exists("license.txt"):
        with open("license.txt", "w", encoding="utf-8") as f:
            f.write("Лицензионное соглашение\n\n")
            f.write("Это программное обеспечение предоставляется как есть.\n")
            f.write("Используйте на свой страх и риск.\n")

    # Сборка приложения настройки (БЕЗ КОНСОЛИ)
    print("3. Сборка приложения настройки...")
    config_cmd = [
        'pyinstaller',
        '--onefile',
        '--noconsole',  # Без консоли для приложения настройки
        '--name=PC_Controller_Config',
        '--hidden-import=tkinter',
        '--hidden-import=psutil',
        '--hidden-import=re',
        '--hidden-import=subprocess',
        '--hidden-import=winreg',
        '--hidden-import=requests',
        'config_app.py'
    ]

    if not run_command(' '.join(config_cmd)):
        print("Ошибка сборки приложения настройки!")
        return

    # Сборка бота (С КОНСОЛЬЮ для видимого режима)
    print("4. Сборка основного бота (с консолью)...")
    bot_cmd = [
        'pyinstaller',
        '--onefile',
        '--noconsole',
        '--name=PC_Controller_Bot',
        '--hidden-import=aiogram',
        '--hidden-import=pyautogui',
        '--hidden-import=psutil',
        '--hidden-import=winapps',
        '--hidden-import=logging',
        '--add-data=functions.py;.',
        '--add-data=callbacks.py;.',
        '--add-data=config.py;.',
        '--add-data=kbs.py;.',
        'run.py'
    ]

    if not run_command(' '.join(bot_cmd)):
        print("Ошибка сборки бота!")
        return

    # Создаем папку для установщика
    print("5. Создание установочного пакета...")
    if os.path.exists("installer_package"):
        shutil.rmtree("installer_package")
    os.makedirs("installer_package")

    # Копируем файлы
    print("6. Копирование файлов...")
    files_to_copy = [
        ("dist/PC_Controller_Config.exe", "installer_package/"),
        ("dist/PC_Controller_Bot.exe", "installer_package/"),
        ("requirements.txt", "installer_package/"),
        ("license.txt", "installer_package/")
    ]

    # Копируем исходные файлы для резервного запуска
    source_files = ['run.py', 'functions.py', 'callbacks.py', 'config.py', 'kbs.py']
    for file in source_files:
        if os.path.exists(file):
            shutil.copy(file, "installer_package/")
            print(f"  Скопирован: {file}")

    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"  Скопирован: {src}")
        else:
            print(f"  Предупреждение: {src} не найден")

    # Создаем bat файл для установки зависимостей
    with open("installer_package/install_dependencies.bat", "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("echo Установка зависимостей PC Controller Bot...\n")
        f.write("echo ==========================================\n")
        f.write("pip install -r requirements.txt\n")
        f.write("if %errorlevel% == 0 (\n")
        f.write("    echo.\n")
        f.write("    echo Зависимости успешно установлены!\n")
        f.write("    echo Запустите PC_Controller_Config.exe для настройки бота\n")
        f.write(") else (\n")
        f.write("    echo.\n")
        f.write("    echo Ошибка установки зависимостей!\n")
        f.write(")\n")
        f.write("pause\n")

    # Создаем инструкцию
    with open("installer_package/INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
        f.write("ИНСТРУКЦИЯ ПО УСТАНОВКЕ PC CONTROLLER BOT\n")
        f.write("=========================================\n\n")
        f.write("1. Скопируйте ВСЕ файлы из этой папки в одну папку на компьютере\n")
        f.write("2. Убедитесь, что установлен Python 3.7+\n")
        f.write("3. Запустите install_dependencies.bat для установки зависимостей\n")
        f.write("4. Запустите PC_Controller_Config.exe для настройки бота\n")
        f.write("5. Получите токен бота у @BotFather в Telegram\n")
        f.write("6. Нажмите 'Проверить токен' для проверки корректности\n")
        f.write("7. Сохраните настройки и запустите бота\n\n")
        f.write("Режимы запуска:\n")
        f.write("- 'Запустить бота (скрыто)' - бот работает в фоне без окна\n")
        f.write("- 'Запустить бота (видимо)' - открывается консольное окно для отладки\n\n")
        f.write("ВАЖНО: Все файлы должны находиться в одной папке!\n\n")
        f.write("Формат токена: 1234567890:ABCDEFGhIjKlMnOpQrStUvWxYz\n")
        f.write("(цифры:длинный_секретный_ключ)\n\n")
        f.write("Краткая инструкция:\n")
        f.write("- Получите токен бота у @BotFather\n")
        f.write("- Узнайте ваш ID у @userinfobot\n")
        f.write("- Настройте бота через PC_Controller_Config.exe\n")
        f.write("- Проверьте токен перед запуском\n")
        f.write("- Включите автозагрузку в настройках\n")
        f.write("- Для отладки используйте видимый режим запуска\n\n")
        f.write("Для автоматической установки зависимостей запустите install_dependencies.bat\n")

    print("7. Создание ZIP архива...")
    shutil.make_archive("PC_Controller_Bot_v1.0", 'zip', "installer_package")

    print("\n" + "=" * 50)
    print("✅ Сборка завершена успешно!")
    print("📦 Создан архив: PC_Controller_Bot_v1.0.zip")
    print("📍 Содержимое архива готово к распространению")
    print("=" * 50)


if __name__ == "__main__":
    build_installer()