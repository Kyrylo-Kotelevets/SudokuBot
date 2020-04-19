from codecs import open
import datetime
import sudoku
import shutil
import time
import os

# Корневая (рабочая) директория
root = 'C:\\Users\\HP_650\\Desktop\\Python_BOT' + os.sep
# Путь к 
others = root + 'others' + os.sep
# Путь к методам решения
method = root + 'methods' + os.sep
# Путь к рекордному времени
record = root + 'records' + os.sep
# Путь к базе данных
path = root + 'DATABASE' + os.sep
# Формат времени
format = '%Y/%m/%d %H:%M:%S.%f'
# Список файлов с данными
data_files = {'current':       'current.txt',
              'gamemode':      'gamemode.txt',
              'history':       'history.txt',
              'last activity': 'last_activity.txt',
              'last alert':    'last_alert.txt',
              'level':         'level.txt',
              'puzzle':        'puzzle.txt',
              'solution':      'solution.txt',
              'score':         'score.txt',
              'start':         'start.txt'}

# Режимы игры
game_modes = ['challenge', 'freeplay']
# Максимальный объем истории пользователя
history_count = 20
# Максимальное время для записи
max_time = '59:59.999999'


# Преобразование разницы во времени к строке с ограничением
def convert(delta) -> str: 
    if delta.seconds // 3600:
        return max_time
    else:
        return f'{delta.seconds // 60:02}:{delta.seconds % 60:02}.{delta.microseconds:06}'


# Сжатие судоку для записи в файл
def compressPuzzle(puzzle: list) -> str:
    ans = ''
    for row in puzzle:
        for num in row:
            ans += str(num)
    return ans


def decompressPuzzle(puzzle: str) -> list:
	return [[int(puzzle[i * 9 + j]) for j in range(9)] for i in range(9)]


# Проверка на существование пользователя
def isUserExist(username) -> bool:
    return os.path.exists(path + username)


# Добавление пользователя в базу данных
def addUser(id, username):
    if isUserExist(username):
        raise Exception('Пользователь уже зарегестрирован')

    os.mkdir(path + username)
    with open(path + username + '/' + 'id.txt', 'w') as file:
        file.write(str(id))
    with open(path + username + '/' + 'history.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'level.txt', 'w') as file:
        file.write(str(sudoku.MIN_LEVEL))
    with open(path + username + '/' + 'start.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'puzzle.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'current.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'solution.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'last_activity.txt', 'w') as file:
        file.write(datetime.datetime.today().strftime(format))
    with open(path + username + '/' + 'last_alert.txt', 'w') as file:
        file.write(datetime.datetime.today().strftime(format))
    with open(path + username + '/' + 'score.txt', 'w') as file:
        file.write('0')
    with open(path + username + '/' + 'gamemode.txt', 'w') as file:
        file.write('challenge')


# Сброс данных пользователя к базовым
def resetUser(username):
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'history.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'level.txt', 'w') as file:
        file.write(str(sudoku.MIN_LEVEL))
    with open(path + username + '/' + 'start.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'puzzle.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'current.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'solution.txt', 'w') as file:
        pass
    with open(path + username + '/' + 'last_activity.txt', 'w') as file:
        file.write(datetime.datetime.today().strftime(format))
    with open(path + username + '/' + 'last_alert.txt', 'w') as file:
        file.write(datetime.datetime.today().strftime(format))
    with open(path + username + '/' + 'score.txt', 'w') as file:
        file.write('0')
    with open(path + username + '/' + 'gamemode.txt', 'w') as file:
        file.write('challenge')


def deleteUser(username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    shutil.rmtree(path + username)
    #os.rmdir(path + username)


# Проверка того, играет ли пользователь
def isUserPlay(username) -> bool:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'start.txt', 'rt') as file:
        return (file.read() != '')


# Получение режима игры пользователя
def getID(username: str) -> str:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'id.txt', 'rt') as file:
        return int(file.read())


# Получение режима игры пользователя
def getGamemode(username: str) -> str:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'gamemode.txt', 'rt') as file:
        return file.read()


# Установка режима игры пользователя
def setGamemode(mode: str, username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if mode not in game_modes:
        raise Exception('Некорректный режим')

    with open(path + username + '/' + 'gamemode.txt', 'w') as file:
        file.write(mode)


# Получение последнего оповещения пользователя
def getLastUserAlert(username: str):
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'last_alert.txt', 'tr') as file:
        return datetime.datetime.strptime(file.read(), format)


# Установка/обновление последнего оповещения пользователя
def udateLastUserAlert(username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'last_alert.txt', 'w') as file:
        file.write(datetime.datetime.today().strftime(format))


# Получение последней активности пользователя
def getLastUserActivity(username: str):
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'last_activity.txt', 'tr') as file:
        return datetime.datetime.strptime(file.read(), format)


# Установка/обновление последней активности пользователя
def udateLastUserActivity(username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'last_activity.txt', 'w') as file:
        file.write(datetime.datetime.today().strftime(format))


# Получение судоку пользователя
def getUserPuzzle(username: str) -> list:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if not isUserPlay(username):
        raise Exception('Пользователь не начал игру')

    with open(path + username + '/' + 'puzzle.txt', 'tr') as file:
        return decompressPuzzle(file.read())


# Обновление судоку (после подсказки)
def updateUserPuzzle(row: int, col: int, username: str) -> None:
	if not isUserExist(username):
		raise Exception('Пользователь не зарегестрирован')
	if not isUserPlay(username):
		raise Exception('Пользователь не начал игру')
	if (row < 0 or row > 8) or (col < 0 or col > 8):
		raise Exception(f'Некорректные координаты [{row}][{col}]\n')

	puzzle = getUserPuzzle(username)
	current = getUserCurrent(username)
	if puzzle[row][col] != 0:
		raise Exception(f'Клетка [{row}][{col}] уже заполнена числом {puzzle[row][col]}')

	puzzle[row][col] = getUserSolution(username)[row][col]
	current[row][col] = getUserSolution(username)[row][col]
	with open(path + username + '/' + 'puzzle.txt', 'w') as file:
		file.write(compressPuzzle(puzzle))
	with open(path + username + '/' + 'current.txt', 'w') as file:
		file.write(compressPuzzle(current))


# Получение нерешенного судоку пользователя
def getUserCurrent(username) -> list:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if not isUserPlay(username):
        raise Exception('Пользователь не начал игру')

    with open(path + username + '/' + 'current.txt', 'tr') as file:
        return decompressPuzzle(file.read())


# Установка нерешенного судоку пользователя
def setUserCurrent(puzzle: list, username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if not isUserPlay(username):
        raise Exception('Пользователь не начал игру')
    if not sudoku.are_equal(puzzle, getUserPuzzle(username)):
        raise Exception('Судоку не совпадает с начальным')
        
    with open(path + username + '/' + 'current.txt', 'w') as file:
        file.write(compressPuzzle(puzzle))


# Получение решенного судоку пользователя
def getUserSolution(username) -> list:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if not isUserPlay(username):
        raise Exception('Пользователь не начал игру')

    with open(path + username + '/' + 'solution.txt', 'tr') as file:
        return decompressPuzzle(file.read())


# Следующее судоку для пользователя
def nextPuzzle(username) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    puzzle = sudoku.getLevelPuzzle(int(getUserLevel(username)))
    solution = sudoku.solve(puzzle)

    with open(path + username + '/' + 'puzzle.txt', 'w') as file:
        file.write(compressPuzzle(puzzle))
    with open(path + username + '/' + 'current.txt', 'w') as file:
        file.write(compressPuzzle(puzzle))
    with open(path + username + '/' + 'solution.txt', 'w') as file:
        file.write(compressPuzzle(solution))


# Проверка правильности пользовательского решения
def isCorrectSolution(puzzle, username) -> bool:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    return puzzle == getUserSolution(username)


# Получение текущего уровня пользователя
def getUserLevel(username) -> float:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'level.txt', 'tr') as file:
        return float(file.read())


# Установка уровня пользователя
def setUserLevel(level, username) -> list:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    level = max(sudoku.MIN_LEVEL, min(sudoku.MAX_LEVEL, level))
    with open(path + username + '/' + 'level.txt', 'w') as file:
        file.write(str(level))


# Обновление уровня пользователя
def updateUserLevel(delta, username) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    setUserLevel(getUserLevel(username) + delta, username)


# Получение очков пользователя
def getUserScore(username) -> int:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'score.txt', 'tr') as file:
        return int(file.read())


# Установка очков пользователя
def setUserScore(score: float, username: int) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'score.txt', 'w') as file:
        file.write(f'{round(score)}')


# Обновление очков пользователя
def updateUserScore(delta: float, username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    setUserScore(max(0, getUserScore(username) + delta), username)


# Получение времени пользователя
def getUserTime(username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if not isUserPlay(username):
        raise Exception('Пользователь не начал игру')

    with open(path + username + '/' + 'start.txt', 'tr') as file:
        return datetime.datetime.strptime(file.read(), format)


# Установка времени пользователя
def setUserTime(time, username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'start.txt', 'w') as file:
        file.write(time.strftime(format))


# Установка времени пользователя
def solvingTime(username: str):
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if not isUserPlay(username):
        raise Exception('Пользователь не начал игру')

    with open(path + username + '/' + 'start.txt', 'rt') as file:
        return datetime.datetime.today() - datetime.datetime.strptime(file.read(), format)


# Установка времени пользователя
def str_solvingTime(username: str) -> str:
    return convert(solvingTime(username))


# Сброс времени пользователя
def resetUserTime(username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'start.txt', 'w') as file:
        pass


# Обновление истории игр пользователя
def updateUserHistory(solved: bool, diff: int, delta, grow: float, username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    time = convert(delta)   
    with open(path + username + '/' + 'history.txt', 'rt') as file:
        data = file.read().split('\n')

    if data == ['']:
        with open(path + username + '/' + 'history.txt', 'w') as file:
            file.write(f'{int(solved)} {diff} {time} {grow}')
    elif len(data) < history_count:
        with open(path + username + '/' + 'history.txt', 'a') as file:
            file.write(f'\n{int(solved)} {diff} {time} {grow}')
    else:
        with open(path + username + '/' + 'history.txt', 'w') as file:
            file.write('\n'.join(data[1:]))
            file.write(f'\n{int(solved)} {diff} {time} {grow}')


# Получение истории игр для пользователя
def getUserHistory(username) -> list:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    with open(path + username + '/' + 'history.txt', 'rt') as file:
        return file.read().split('\n')


# Получение истории игр для пользователя
def getUserLevelHistory(username) -> list:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')

    data = []
    with open(path + username + '/' + 'history.txt', 'rt') as file:
        for line in file:
            data.append(float(line.split(' ')[1]))
    return data


# Получение текущего рекорда решения
def get_record(diff: float) -> list:
    if int(diff) not in range(sudoku.MIN_LEVEL, sudoku.MAX_LEVEL + 1):
        raise Exception('Некорректная сложность')

    with open(record + str(int(diff)) + '.txt', 'rt') as file:
        return file.read().split(' ')


# Проверка на установку нового рекорда
def is_new_record(delta, diff: float) -> bool:
    if int(diff) not in range(sudoku.MIN_LEVEL, sudoku.MAX_LEVEL + 1):
        raise Exception('Некорректная сложность')

    delta = f'{delta.seconds // 60:02}:{delta.seconds % 60:02}.{delta.microseconds:06}'
    return delta < get_record(diff)[0]


# Установка нового рекорда решения
def update_record(delta, diff: float, username: str) -> None:
    if not isUserExist(username):
        raise Exception('Пользователь не зарегестрирован')
    if int(diff) not in range(sudoku.MIN_LEVEL, sudoku.MAX_LEVEL + 1):
        raise Exception('Некорректная сложность')
    if delta.seconds // 3600:
        raise Exception('Некорректное время')

    delta = f'{delta.seconds // 60:02}:{delta.seconds % 60:02}.{delta.microseconds:06}'
    if delta >= get_record(int(diff))[0]:
        raise Exception('Время больше текущего')

    with open(record + str(int(diff)) + '.txt', 'w') as file:
        file.write(delta + ' ' + username)


# Список рекордов и пользователей, которые их установили
def records_list() -> list:
    record_list = []

    for diff in range(sudoku.MIN_LEVEL, sudoku.MAX_LEVEL + 1):
        record_list.append([diff] + get_record(diff))
    return record_list


# Общий рейтинг по уровню
def level_rating():
    users = os.listdir(path)
    rating = []

    for user in users:
    	if getUserLevel(user) > sudoku.MIN_LEVEL:
    		rating.append([user, getUserLevel(user)])
    rating.sort(key=lambda x: x[1], reverse=True)
    return rating


# Общий рейтинг по количеству очков
def score_rating():
    users = os.listdir(path)
    rating = []

    for user in users:
    	if getUserScore(user) > 0:
    		rating.append([user, getUserScore(user)])
    rating.sort(key=lambda x: x[1], reverse=True)
    return rating


# Список пользователей без активности за последние сутки
def unactive_users(time: int = 1) -> list:
    current_time = datetime.datetime.today()
    unactive = []

    for user in os.listdir(path):
        if (current_time - getLastUserActivity(user)).days >= time:
            unactive.append(user)

    return unactive


# Возвращает описание метода решения
def get_method_description(name: str, num: str = '') -> str:
    with open(method + name + os.sep + 'description' + num + '.txt', 'r', encoding='utf-8') as file:
        return file.read()


# Возвращает список методов решения судоку и их описания
def get_methods_list() -> str:
    with open(method + 'methods_list.txt', 'r', encoding='utf-8') as file:
        return file.read()

#addUser('@Test_bot')
#print(isUserExist('@WeNoM_21'))    
#nextPuzzle('@WeNoM_21')
#print((datetime.datetime.today() - getUserTime('@WeNoM_21')))
#setUserTime(datetime.datetime.today(), '@WeNoM_21')
#updateUserHistory(getUserLevel('@WeNoM_21'), 180, -3, '@WeNoM_21')

#print(getUserTime('@WeNoM_21').strftime(format))
#resetUserTime('@WeNoM_21')
#print(isUserPlay('@WeNoM_21'))

#print(sudoku.getStrPuzzle(getUserPuzzle('@WeNoM_21')))
#print(sudoku.getStrPuzzle(getUserSolution('@WeNoM_21')))
#print(getUserHistory('@WeNoM_21'))

#print(level_rating())

#print(os.listdir(path))
#python C:\Users\HP_650\Desktop\Python_BOT\database.py

if __name__ != '__main__':
    print('Модуль СУБД подключен и работает исправно')
