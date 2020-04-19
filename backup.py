from datetime import datetime
from shutil import make_archive
import time
import re
import os

# Путь к рабочей директории
PATH = 'C:\\Users\\HP_650\\Desktop\\Python_BOT'

# Целевая директория
TARGET = PATH + os.sep + 'BACKUP'
# Исходная директория
SOURCE = PATH + os.sep + 'DATABASE'

#
date_f = '%d.%m.%Y'
#
time_f = '%H.%M.%S'

# Регулярное выражение, чтобы бэкап происходил каждые 10 минут
pattern = re.compile(r'[0-9][0-9].[0-9]0.00')


# Функция архивации (работает бесконечно)
def start() -> None:
    print('Резервное копирование запущено ' + datetime.now().strftime(date_f + ' ' + time_f))
    while(True):
        # Текущая дата в нужном формате
        today_date = datetime.now().strftime(date_f)
        # Текущее время в нежном формате
        today_time = datetime.now().strftime(time_f)

        # Если время кратно десяти минутам
        if pattern.match(today_time):
            # Создаем zip-архив всей БД
            make_archive(TARGET + os.sep + today_date + os.sep + today_time, 'zip', SOURCE)
            print(f'Резервная копия СОЗДАНА ({today_date}, {today_time})')
            # И приостановим процесс на 10 минут
            time.sleep(10 * 60)


start()
# python C:\Users\HP_650\Desktop\Python_BOT\backup.py
