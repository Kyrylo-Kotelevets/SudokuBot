from random import randint, random
import copy

# Минимально и максимально возможные уровни
MIN_LEVEL, MAX_LEVEL = 10, 62

# Оценка уровня судоку относительно сложности
def getLevel(diff: int) -> str:
    if diff in range(MIN_LEVEL, 15):
        return 'very easy'
    elif diff in range(15, 25):
        return 'easy'
    elif diff in range(25, 40):
        return 'medium'
    elif diff in range(40, 50):
        return 'hard'
    elif diff in range(50, MAX_LEVEL + 1):
        return 'extreme'
    else:
        raise Exception("Некорректная сложность")


# Оценка ранга игрока относительно сложности
def getRank(diff: int) -> str:
    if diff in range(MIN_LEVEL, 15):
        return 'noob'
    elif diff in range(15, 25):
        return 'beginner'
    elif diff in range(25, 40):
        return 'middle'
    elif diff in range(40, 50):
        return 'advanced'
    elif diff in range(50, MAX_LEVEL + 1):
        return 'master'
    else:
        raise Exception("Некорректная сложность")


# Получение судоку, заполненного нулями
def getEmpty() -> list:
    return [[0] * 9 for row in range(9)]


# Получение примера заполненного судоку
def getExample() -> list:
    # Базовый набор чисел
    base = [num for num in range(1, 10)]
    puzzle = []

    for i in range(3):
        for j in range(3):
            #  Сдвигаем базовый набор чисел и складываем
            puzzle.append(base[i + j * 3:] + base[:i + j * 3])
    return puzzle


# Начальное состояние для перемешивания
def getBasePuzzle() -> list:
    return [[2, 9, 3, 4, 5, 7, 6, 8, 1], [4, 7, 5, 1, 8, 6, 3, 9, 2], [1, 6, 8, 3, 9, 2, 7, 4, 5], [9, 4, 2, 5, 7, 1, 8, 6, 3], [3, 8, 1, 6, 2, 9, 5, 7, 4], [6, 5, 7, 8, 3, 4, 1, 2, 9], [7, 2, 6, 9, 1, 3, 4, 5, 8], [5, 1, 4, 2, 6, 8, 9, 3, 7], [8, 3, 9, 7, 4, 5, 2, 1, 6]]



# Проверка судоку на решенность
def isSolved(puzzle: list) -> bool:
    # Проверяем на факт того, что все клетки заполнены
    return all(num != 0 for row in puzzle for num in row)


# Подсчет пустых клеток в головоломке
def valuation(puzzle: list) -> int:
    return sum(row.count(0) for row in puzzle)


# Подсчет пустых клеток в головоломке
def are_equal(user_puzzle: list, initial_puzzle: list) -> bool:
    for i in range(9):
        for j in range(9):
            if initial_puzzle[i][j] != 0 and user_puzzle[i][j] != initial_puzzle[i][j]:
                return False
    return True


# Проверка наличия повторов
def isCorrect(puzzle: list) -> bool:
    for i in range(9):
        for j in range(9):
            # Если клетка не заполнена
            if puzzle[i][j] == 0:
                continue

            for k in range(9):
                # Если есть повтор в строке
                if puzzle[i][k] == puzzle[i][j] and k != j:
                    return False
                # Если есть повтор в столбце
                if puzzle[k][j] == puzzle[i][j] and k != i:
                    return False

            row = 3 * (i // 3)
            col = 3 * (j // 3)
            for r in range(row, row + 3):
                for c in range(col, col + 3):
                    # Если есть повтор в квадрате
                    if puzzle[r][c] == puzzle[i][j] and (r != i or c != j):
                        return False
    return True


# Главная сборочная функция
def solve(puzzle: list) -> list:
    # Копируем исходное судоку
    solution = copy.deepcopy(puzzle)
    # Если решение существует
    if solveHelper(solution):
        return solution
    # Решения не существует
    return None


#  Математический аппарат
def solveHelper(solution: list) -> bool:
    # Минимальное множество возможных чисел
    MIN = None
    while True:
        MIN = None
        for row in range(9):
            for col in range(9):
                # Если клетка пуста, то продолжаем
                if solution[row][col] != 0:
                    continue

                # Получаем  множество чисел для клетки
                possible = find_pos(row, col, solution)
                # Размер множества чисел
                count = len(possible)

                # Множество пусто, текущее состояние нерешаемо
                if count == 0:
                    return False
                # Если возможно только одно число, то вставим
                if count == 1:
                    solution[row][col] = possible.pop()
                # Если минимальное множество пусто или больше
                if not MIN or count < len(MIN[1]):
                    MIN = ((row, col), possible)

        # Если множество пусто, то судоку собрано
        if not MIN:
            return True
        # Если больше нет однозначных чисел для вставки
        elif len(MIN[1]) > 1:
            break

    # Координаты клетки с минимальным множеством
    r, c = MIN[0]

    # Перебираем все числа из множества
    for v in MIN[1]:
        # Сохраняем копию текущего состояния
        solutionCopy = copy.deepcopy(solution)
        # Запоняем клетку теекущим числом из множества
        solutionCopy[r][c] = v
        # Если рекурсивный поиск был удачным
        if solveHelper(solutionCopy):
            for r in range(9):
                for c in range(9):
                    solution[r][c] = solutionCopy[r][c]
            return True
    return False


# Число возможных решений судоку
def solutions(puzzle: list) -> int:
    return numOfSolutions(copy.deepcopy(puzzle))


# Мат. аппарат для пересчёта решений
def numOfSolutions(solution: list) -> int:
    MIN = None
    while True:
        MIN = None
        for row in range(9):
            for col in range(9):
                # Если клетка пуста, то продолжаем
                if solution[row][col] != 0:
                    continue

                # Получаем  множество чисел для клетки
                possible = find_pos(row, col, solution)
                # Размер множества чисел
                count = len(possible)

                # Множество пусто, решений нет
                if count == 0:
                    return 0
                # Если возможно только одно число, то вставим
                if count == 1:
                    solution[row][col] = possible.pop()
                # Если минимальное множество пусто или больше
                if not MIN or count < len(MIN[1]):
                    MIN = ((row, col), possible)
        # Если множество пусто, то судоку собрано
        if not MIN:
            return 1
        # Если больше нет однозначных чисел для вставки
        elif len(MIN[1]) > 1:
            break

    # Координаты клетки с минимальным множеством
    r, c = MIN[0]

    # Изначально решений текущего состояния нет
    res = 0

    # Перебираем все числа из множества
    for v in MIN[1]:
        # Сохраняем копию текущего состояния
        solutionCopy = copy.deepcopy(solution)
        # Запоняем клетку теекущим числом из множества
        solutionCopy[r][c] = v
        # Прибавляем решения следующего состояния
        res += numOfSolutions(solutionCopy)
    return res


# Получение множества возможных чисел для позиции в виде блока
def get_block_possible(row: int, col: int, puzzle: list) -> dict:
    block = [[0] * 3 for i in range(3)]

    for num in find_pos(row, col, puzzle):
        block[(num - 1) // 3][(num - 1) % 3] = num
    return block


# Получение всех множеств для вставки
def find_all_pos(puzzle: list):
    return [[find_pos(i, j, puzzle) for j in range(9)] for i in range(9)]

# Получение множества возможных чисел для позиции
def find_pos(row: int, col: int, puzzle: list) -> dict:
    if puzzle[row][col] != 0:
        return None
    else:
        values = {v for v in range(1, 10)}
        values -= getRowValues(row, puzzle)
        values -= getColValues(col, puzzle)
        values -= getBlockValues(row, col, puzzle)
        return values


# Получение возможных чисел для row-той строки
def getRowValues(row: int, puzzle: list) -> dict:
    return set(puzzle[row][:])


# Получение возможных чисел для col-того столбца
def getColValues(col: int, puzzle: list) -> dict:
    return {puzzle[r][col] for r in range(9)}


# Получение возможных чисел квадрата
def getBlockValues(row: int, col: int, puzzle: list) -> dict:
    # Координаты начала блока
    row = 3 * (row // 3)
    col = 3 * (col // 3)
    return {puzzle[row + r][col + c] for r in range(3) for c in range(3)}


# Свап двух разных строк в одном квадранте
def swap_rows(puzzle: list) -> None:
    R1 = randint(0, 8)
    R2 = randint((R1 // 3) * 3, (R1 // 3) * 3 + 2)
    while R1 == R2:
        R2 = randint((R1 // 3) * 3, (R1 // 3) * 3 + 2)

    puzzle[R1][:], puzzle[R2][:] = puzzle[R2][:], puzzle[R1][:]


# Свап двух разных столбцов в одном квадранте
def swap_cols(puzzle: list) -> None:
    С1 = randint(0, 8)
    С2 = randint((С1 // 3) * 3, (С1 // 3) * 3 + 2)
    while С1 == С2:
        С2 = randint((С1 // 3) * 3, (С1 // 3) * 3 + 2)

    for i in range(9):
        puzzle[i][С1], puzzle[i][С2] = puzzle[i][С2], puzzle[i][С1]


# Свап двух разных блочных строк в одном квадранте
def swap_rows_area(puzzle: list) -> None:
    area1 = randint(0, 2)
    area2 = randint(0, 2)
    while area1 == area2:
        area2 = randint(0, 2)

    for i in range(3):
        puzzle[area1 * 3 + i][:], puzzle[area2 * 3 + i][:] = puzzle[area2 * 3 + i][:], puzzle[area1 * 3 + i][:]


# Свап двух разных блочных столбцов в одном квадранте
def swap_cols_area(puzzle: list) -> None:
    area1 = randint(0, 2)
    area2 = randint(0, 2)
    while area1 == area2:
        area2 = randint(0, 2)

    for j in range(3):
        for i in range(9):
            puzzle[i][area1 * 3 + j], puzzle[i][area2 * 3 + j] = puzzle[i][area2 * 3 + j], puzzle[i][area1 * 3 + j]


# Транспонирование судоку относительно главной диагонали
def main_transpose(puzzle: list) -> None:
    for i in range(9):
        for j in range(i + 1, 9):
            puzzle[i][j], puzzle[j][i] = puzzle[j][i], puzzle[i][j]


# Транспонирование судоку относительно побочной диагонали
def side_transpose(puzzle: list) -> None:
    for i in range(9):
        for j in range(i + 1, 9):
            puzzle[i][j], puzzle[j][i] = puzzle[j][i], puzzle[i][j]


# Набор вероятностей: [0.35/0.35, 0.125/0.125, 0.025/0.025]
# Запутывание/перемешивание судоку
def mix_puzzle(puzzle: list, times: int = 200) -> None:
    # Пока не выполним все нужные перестановки
    for i in range(times):
        # Выбираем случайное число, соответсвующее некоторому изменению
        shuffle = random()

        if shuffle <= 0.7:
            if randint(0, 1) & 1:
                swap_rows(puzzle)
            else:
                swap_cols(puzzle)
        elif shuffle <= 0.95:
            if randint(0, 1) & 1:
                swap_rows_area(puzzle)
            else:
                swap_cols_area(puzzle)
        else:
            if randint(0, 1) & 1:
                main_transpose(puzzle)
            else:
                side_transpose(puzzle)


# Случайная перетасовка судоку
def getMixedPuzzle(times: int = 200) -> list:
    puzzle = getExample()
    mix_puzzle(puzzle, times)
    return puzzle


# Получение судоку для заданного уровня
def getLevelPuzzle(level: int) -> list:
    # Начнём базового состояния
    puzzle = getBasePuzzle()
    # Перемешаем судоку
    mix_puzzle(puzzle)
    # Введем счетчик откатов во избежание зацикливания
    back = 0

    # Пока нужный уровень сложности не достигнут
    while level and back <= 3 ** 3:
        # Выберем случайную клетку
        x, y = randint(0, 8), randint(0, 8)

        # Если выбрали не пустую, то запомним и обнулим
        if puzzle[x][y] != 0:
            temp, puzzle[x][y] = puzzle[x][y], 0

            # Если решенин не единственно, то откат +1
            if solutions(puzzle) != 1:
                puzzle[x][y] = temp
                back += 1
            # Иначе понижаем целевой уровень
            else:
                level -= 1
    return puzzle


# Построчная печать судоку
def getStrPuzzle(puzzle: list) -> str:
    ans = ''
    for row in puzzle:
        ans += str(row) + '\n'
    return ans


###############################################
#######  БРАТИШКА, Я ТЕБЕ ДЕБАГ ПРИНЁС  #######
###############################################

#print(getLevel(randint(0, 66)))
#print(getRank(randint(10, 66)))

#empty_puzzle = getEmpty()
#example_puzzle = getExample()

#print(getStrPuzzle(empty_puzzle))
#print(getStrPuzzle(example_puzzle))

#print(isSolved(empty_puzzle))
#print(isSolved(example_puzzle))

#print(puzzle_valuation(empty_puzzle))
#print(puzzle_valuation(example_puzzle))

#print(isCorrect(empty_puzzle))
#print(isCorrect(example_puzzle))

#example_puzzle[0][0] = 9
#empty_puzzle[0][0] = 9

#print(isCorrect(empty_puzzle))
#print(isCorrect(example_puzzle))

#puzzle = getLevelPuzzle(60)
#print(getStrPuzzle(puzzle))
#print(isCorrect(puzzle))

###############################################
#######  БРАТИШКА, Я ТЕБЕ ДЕБАГ ПРИНЁС  #######
###############################################
#python C:\Users\HP_650\Desktop\Python_BOT\sudoku.py


if __name__ != '__main__':
    print('Модуль мат. аппарата подключен и работает исправно')
