from database import getUserLevelHistory, getUserHistory, getUserLevel, history_count, others
from PIL import Image, ImageDraw, ImageFont
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

im_width = 640
im_height = 560

start_x = 60
start_y = 445
padding = 6
size = (im_width - 2 * start_x - 9 * padding + 15) // (history_count // 2)

poz_color = '#008000'
neu_color = '#bfbfbf'
neg_color = '#e60000'


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

    plt.tick_params(axis='both', which='both', labelsize=15)

    # И, наконец, сохраняем красоту в файл
    plt.savefig(others + 'HISTORY.png')


def paste_history(username: str) -> None:
	def color(c: float) -> str:
		if c < 0:
			return neg_color
		elif c > 0:
			return poz_color
		else:
			return neu_color

	def draw_num(x: int, y: int, num: float):
		if num == -0.0 or num == 0.0:
			drawer.text((x + 3, y + 10), text='  0  ', fill='black', font=ImageFont.truetype(others + 'arial.ttf', 25))
		elif (num < 0):
			drawer.text((x + 5, y + 12), text=f'{num}', fill='black', font=ImageFont.truetype(others + 'arial.ttf', 22))
		else:
			drawer.text((x + 2, y + 12), text=f'+{num}', fill='black', font=ImageFont.truetype(others + 'arial.ttf', 22))

	history = getUserHistory(username)
	change = [min(9.9, round(float(record.split().pop()), 1)) for record in history] + [None] * (history_count - len(history))

	image = Image.new('RGB', (im_width, im_height), '#ffffff')
	image.paste(Image.open(others + 'HISTORY.png'), (0, 0))
	drawer = ImageDraw.Draw(image)

	for i in range(10):
		x1, x2 = start_x + (i * padding) + (i * size), start_x + (i * padding) + ((i + 1) * size)
		if change[i] != None:
			drawer.rectangle([(x1, start_y), (x2, start_y + size)], fill=color(change[i]), outline='black')
			draw_num(x1, start_y, change[i])
		if change[i + 10] != None:
			drawer.rectangle([(x1, start_y + size + padding), (x2, start_y + 2 * size + padding)], fill=color(change[i + 10]), outline='black')
			draw_num(x1, start_y + size + padding, change[i + 10])
	image.save(others + 'HISTORY.png')


def draw(username: str):
	get_graphic(username)
	paste_history(username)


# python C:\Users\HP_650\Desktop\Python_BOT\graphic.py

if __name__ != '__main__':
    print('Модуль отрисовки графика подключен и работает исправно')
