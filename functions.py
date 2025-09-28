import pyautogui
import os
import webbrowser
import psutil
import platform
import winapps
import io
from config import dp, ALLOWED_USERS
from aiogram.types import InputFile


def is_allowed(user_id):
    return str(user_id) in ALLOWED_USERS


async def handle_quick_command(message):
    text = message.text
    try:
        if text == "Громкость +":
            pyautogui.press('volumeup')
            await message.reply('Громкость увеличена')
        elif text == "Громкость -":
            pyautogui.press('volumedown')
            await message.reply('Громкость уменьшена')
        elif text == "Пауза":
            pyautogui.press('playpause')
            await message.reply('Воспроизведение приостановлено')
        elif text == "Продолжить":
            pyautogui.press('playpause')
            await message.reply('Воспроизведение продолжено')
        elif text == "Диспетчер задач":
            os.system("taskmgr")
            await message.reply('Открываю диспетчер задач')
        elif text == "Проводник":
            os.system("explorer")
            await message.reply('Открываю проводник')
        elif text == "Свернуть все":
            pyautogui.hotkey('win', 'd')
            await message.reply('Все окна свернуты')
        elif text == "Обновить":
            await message.reply('Интерфейс обновлен')
    except Exception as e:
        await message.reply(f'Ошибка: {str(e)}')


async def handle_extra_command(message):
    text = message.text
    try:
        if text == "Процессы":
            await top_processes(message)
        elif text == "Диски":
            await disk_info(message)
        elif text == "Сеть":
            await network_info(message)
        elif text == "Батарея":
            await battery_info(message)
        elif text == "Разрешение":
            await screen_resolution(message)
    except Exception as e:
        await message.reply(f'Ошибка: {str(e)}')


async def handle_message(message):
    if not is_allowed(message.from_user.id):
        await message.reply('Отказано в доступе')
        return

    try:
        text = message.text

        if text in ['Скрин']:
            await take_screenshot(message)

        elif text in ['Инфо']:
            await system_info(message)

        elif text in ['Приложения']:
            await list_apps(message)

        elif text.startswith('http'):
            webbrowser.open(message.text)
            await message.reply('Сайт открывается')

        elif text in ['Открой сайт']:
            await message.reply('Отправьте ссылку для открытия сайта')

        elif text in ['Закрой окно']:
            pyautogui.hotkey('alt', 'f4')
            await message.reply('Закрываю активное окно')

        elif text in ['Блокировка']:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            await message.reply('Компьютер заблокирован')

        elif text in ['Сон']:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            await message.reply('Перевожу в режим сна')

        elif text in ['Перезагрузка']:
            await message.reply('Перезагружаю ПК')
            os.system("shutdown /r /t 1")

        elif text.startswith('Открой '):
            app_name = message.text.split(' ', 1)[1]
            await open_application(message, app_name)

        elif text in ['off']:
            await message.reply('Выключаю ПК')
            os.system("shutdown /s /t 1")

    except Exception as e:
        await message.reply(f'Ошибка: {str(e)}')


async def take_screenshot(message):
    try:
        screenshot = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        await message.reply_photo(InputFile(img_bytes, filename='screenshot.png'))
    except Exception as e:
        await message.reply(f'Ошибка скриншота: {str(e)}')


async def system_info(message):
    version_info = get_windows_version()
    res = "Информация о системе\n\n"

    if 'ошибка' in version_info:
        res += f"Ошибка: {version_info['ошибка']}"
    else:
        res += "Windows\n"
        res += f"Платформа: {version_info['платформа']}\n"
        res += f"Версия: {version_info['версия']}\n"
        res += f"Релиз: {version_info['релиз']}\n"

    res += "\nПроизводительность\n"
    res += f"Загрузка CPU: {get_cpu_usage()}%\n"

    memory = get_memory_usage()
    for key, value in memory.items():
        res += f"{key}: {value}\n"

    await message.reply(res)


async def list_apps(message):
    try:
        apps_list = []
        for app in winapps.list_installed():
            name = app.name
            try:
                path = app.install_location or '-'
            except:
                path = '-'
            apps_list.append(f'{name} ({path})')

        app_messages = split_apps_message(apps_list)

        for i, app_message in enumerate(app_messages):
            header = f"Приложения ({i + 1}/{len(app_messages)}):\n\n" if len(app_messages) > 1 else "Приложения:\n\n"
            await message.reply(header + app_message)
    except Exception as e:
        await message.reply(f'Ошибка списка приложений: {str(e)}')


async def open_application(message, app_name):
    try:
        os.startfile(f"{app_name}.exe")
        await message.reply(f'Запускаю {app_name}')
    except Exception as e:
        await message.reply(f'Ошибка запуска: {str(e)}')


async def top_processes(message):
    try:
        processes = get_top_processes(8)
        res = "Топ процессов:\n\n"
        res += "PID | Имя | CPU | Память\n"

        for proc in processes:
            res += f"{proc[0]} | {proc[1][:20]} | {proc[2]} | {proc[3]}\n"

        await message.reply(res)
    except Exception as e:
        await message.reply(f'Ошибка процессов: {str(e)}')


async def disk_info(message):
    try:
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'total': usage.total / (1024 ** 3),
                    'used': usage.used / (1024 ** 3),
                    'free': usage.free / (1024 ** 3),
                    'percent': usage.percent
                })
            except:
                continue

        res = "Диски:\n\n"
        for disk in disks:
            res += f"{disk['device']}\n"
            res += f"Всего: {disk['total']:.1f} ГБ\n"
            res += f"Использовано: {disk['used']:.1f} ГБ ({disk['percent']}%)\n"
            res += f"Свободно: {disk['free']:.1f} ГБ\n\n"

        await message.reply(res)
    except Exception as e:
        await message.reply(f'Ошибка дисков: {str(e)}')


async def network_info(message):
    try:
        networks = psutil.net_io_counters(pernic=True)
        res = "Сеть:\n\n"

        for interface, stats in networks.items():
            res += f"{interface}\n"
            res += f"Отправлено: {stats.bytes_sent / (1024 ** 2):.1f} МБ\n"
            res += f"Получено: {stats.bytes_recv / (1024 ** 2):.1f} МБ\n\n"

        await message.reply(res)
    except Exception as e:
        await message.reply(f'Ошибка сети: {str(e)}')


async def battery_info(message):
    try:
        battery = psutil.sensors_battery()
        if battery:
            res = "Батарея:\n\n"
            res += f"Заряд: {battery.percent}%\n"
            res += f"Статус: {'Заряжается' if battery.power_plugged else 'Разряжается'}\n"
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                res += f"Осталось: {battery.secsleft // 3600} ч. {(battery.secsleft % 3600) // 60} мин.\n"
        else:
            res = "Батарея не найдена"
    except:
        res = "Ошибка батареи"

    await message.reply(res)


async def screen_resolution(message):
    try:
        width, height = pyautogui.size()
        await message.reply(f"Разрешение: {width} x {height}")
    except Exception as e:
        await message.reply(f'Ошибка разрешения: {str(e)}')


def get_windows_version():
    try:
        return {
            'платформа': platform.platform(),
            'версия': platform.version(),
            'релиз': platform.release(),
            'система': platform.system()
        }
    except Exception as e:
        return {'ошибка': str(e)}


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        'Всего': f'{memory.total / (1024 ** 3):.2f} ГБ',
        'Используется': f'{memory.used / (1024 ** 3):.2f} ГБ',
        'Свободно': f'{memory.available / (1024 ** 3):.2f} ГБ',
        'Процент использования': f'{memory.percent}%'
    }


def get_top_processes(n=10):
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                       key=lambda x: x.info['cpu_percent'] or 0,
                       reverse=True)[:n]:
        try:
            processes.append([
                proc.info['pid'],
                proc.info['name'],
                f"{proc.info['cpu_percent'] or 0:.2f}%",
                f"{proc.info['memory_percent'] or 0:.2f}%"
            ])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def split_apps_message(apps_list, max_length=4000):
    messages = []
    current_message = ""

    for app in apps_list:
        app_line = f"{app}\n"
        if len(current_message) + len(app_line) > max_length:
            messages.append(current_message)
            current_message = app_line
        else:
            current_message += app_line

    if current_message:
        messages.append(current_message)

    return messages