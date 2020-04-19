from database import getUserLevelHistory, getUserLevel
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from database import others


# Основная функция отрисовки и сохранения графика
def get_graphic(username: str) -> None:
    # Получение истории изменений уровня пользователя
    y = getUserLevelHistory(username) + [getUserLevel(username)]

    fig, ax = plt.subplots()
    # Создание графика
    ax.plot(y, color='dodgerblue')

    # ОЧень красивое заглавие графика
    ax.set_title('История игр', fontsize=20)
    # Подпись оси ординат
    ax.set_ylabel('Уровень')

    # Диапазон значений оси ординат
    ax.set_ylim(min(y) - 5, max(y) + 5)
    # Диапазон значений оси абсцисс
    ax.set_xlim(0, len(y) - 1)

    # Сокрытие всех осей, кроме оси ординат
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Убираем числа с оси абсцисс
    ax.set_xticklabels([])

    # Делаем красивую (не очень) заливку области под графиком
    ax.fill_between(range(0, len(y)), y, color='lightskyblue')

    # Устанаваем нужные разметки
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

    # И, наконец, сохраняем красоту в файл
    plt.savefig(others + 'HISTORY.png')


if __name__ != '__main__':
    print('Модуль отрисовки графика подключен и работает исправно')
