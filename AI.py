import datetime
import database
import math

# Время, необходимое для вписывания одного числа в нужную клетку
PROCESSING = 5 / 60
# Ну сложности судоку все те же
Diff = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]


# Минимальное оценочное время для решения судоку
min_time = lambda dif: 1.5 * math.exp(0.0334 * dif - 0.3179) + dif * PROCESSING
# Максимальное оценочное время для решения судоку
max_time = lambda dif: 1.5 * math.exp(0.0386 * dif - 0.2876) + dif * PROCESSING
# Среднее оценочное время для решения судоку
avg_time = lambda dif: (min_time(dif) + max_time(dif)) / 2

# Гасящий коефициент для времени решения
growKoef = lambda dif: 0.00025 * (dif ** 2) + 0.8

# Коефициент прироста баллов
scoreKoef = lambda dif: 0.04 * dif + 0.6
# Коефициент прироста баллов
difKoef = lambda dif: math.exp(0.0468 * dif - 2.821)

# Прирост очков пользователя за решение головоломки
scoreChange = lambda dif: round(scoreKoef(dif) * difKoef(dif), 3) * (10 ** 4)

# Нормализированное распределение пересчета уровня
diffChange = lambda x: 10 - math.exp(-0.4 * x * x) / (0.0399 * math.sqrt(2 * math.pi))


# Коефициент штрафа за открытую клетку
cell_penalty_koef = 0.25
# Коефициент штрафа за полную проверку
check_penalty_koef = 0.5


# Пересчет уровня пользователя после решения судоку
def Change(time: float, diff: float) -> float:
    if time - avg_time(diff) > 0:
        return -diffChange((time - avg_time(diff)) / growKoef(diff)) * 0.5
    else:
        return diffChange((time - avg_time(diff)) / growKoef(diff))


# Начисление штрафного времени за открытую ячейку
def cell_penalty(username: str):
    penalty = datetime.timedelta(minutes=avg_time(database.getUserLevel(username)) * cell_penalty_koef)
    database.setUserTime(database.getUserTime(username) - penalty, username)


# Начисление штрафного времени за полную проверку
def check_penalty(username: str):
    penalty = datetime.timedelta(minutes=avg_time(database.getUserLevel(username)) * check_penalty_koef)
    database.setUserTime(database.getUserTime(username) - penalty, username)


# Начисление штрафа сдавшемуся пользователю
def GiveUpChange(time: float, diff: float) -> float:
    return -diffChange(time / growKoef(diff)) * 0.5


# Пересчёт уровня пользователя после решения судоку
def recount_level(username: str, gived_up: bool=False) -> None:
    diff = database.getUserLevel(username)
    time = database.solvingTime(username)

    # Если пользователь сдался, то отнимем смягченно баллы
    if gived_up:
        delta = GiveUpChange(time.seconds / 60, diff)
    else:
        delta = Change(time.seconds / 60, diff)

    # Если играл без времени, то не штрафуем
    if database.getGamemode(username) == 'freeplay':
        database.updateUserScore(scoreChange(diff), username)
        database.updateUserHistory(not gived_up, round(diff, 2), time, 0, username)
    elif database.getGamemode(username) == 'challenge':
        database.updateUserLevel(delta, username)
        database.updateUserScore(scoreChange(diff), username)
        database.updateUserHistory(not gived_up, round(diff, 2), time, round(delta, 2), username)
    else:
        pass


#python C:\Users\HP_650\Desktop\Python_BOT\AI.py

if __name__ != '__main__':
    print('Модуль ИИ подключен и работает исправно')
