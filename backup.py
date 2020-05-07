from datetime import datetime, timedelta
from shutil import make_archive
from os import sep, makedirs
from time import sleep 
from re import compile

# Путь к рабочей директории
PATH = 'C:\\Users\\HP_650\\Desktop\\Python_BOT'

# Целевая директория
TARGET = PATH + sep + 'BACKUP'
# Исходная директория
SOURCE = {'database' : PATH + sep + 'DATABASE', 'stats' : PATH + sep + 'statistic', 'records' : PATH + sep + 'records'}
# Промежуток архивации в минутах
EVERY = 10

# Формат даты
date_f = '%d.%m.%Y'
# Формат времени
time_f = '%H.%M.%S'

# Регулярное выражение, чтобы бэкап происходил каждые 10 минут
pattern = compile(r'[0-9][0-9].[0-9]0.00')
# Настоящий момент времени для вывода в консоль
Now = f'({datetime.now().strftime(date_f)}, {datetime.now().strftime(time_f)})'


# Функция архивации (работает бесконечно)
def run() -> None:
    print(f'Архивация запущена {Now}')
    while True:
        # Фиксруем текущий момент времени
        current = datetime.now()
        # Текущая дата в нужном формате
        today_date = current.strftime(date_f)
        # Текущее время в нежном формате
        today_time = current.strftime(time_f)

        # Если время кратно десяти минутам
        if pattern.match(today_time):
            # Создаем директорию для хранения копий
            makedirs(TARGET + sep + today_date + sep + today_time)

            # Создаем zip-архив выбрвнных частей БД
            for directory in SOURCE.keys():
                make_archive(TARGET + sep + today_date + sep + today_time + sep + directory, 'zip', SOURCE[directory])

            print(f'Резервная копия СОЗДАНА ({today_date}, {today_time})')
            sleep(EVERY * 60 - 10)
        else:
            delta = datetime.strptime(today_date + today_time[:-4] + '0', date_f + time_f[:-3]) + timedelta(minutes=10) - current
            sleep(max(0, delta.seconds - 1))


# python C:\Users\HP_650\Desktop\Python_BOT\backup.py

if __name__ != '__main__':
    print(f'Модуль архивации подключен и работает исправно')
