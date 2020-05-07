from PIL import Image, ImageDraw, ImageFont
from database import others, decompressPuzzle
from random import randint
import sudoku
import copy

b_border = 18
s_border = 8
width = 200
im_size = width * 9 + s_border * 6 + b_border * 4
pos_width = 60

X = lambda x: b_border * (x // 3) + s_border * (x - x // 3) + x * width
Y = lambda y: b_border * (y // 3) + s_border * (y - y // 3) + y * width
R = lambda x, y: [(x + s_border, y + s_border), (x + b_border + width, y + b_border + width)] 
C = lambda x, y: [(x + 3 * s_border, y + 3 * s_border), (x + b_border - 2 * s_border + width, y + b_border - 2 * s_border + width)] 


THEMES = {
	'classic' : {
		'possible_color' : ['#ffffff', '#ff0003', '#ff8a00', '#fff000', '#7dff00', '#00c000', '#00fbf3', '#2447ff', '#000297', '#4e006c'], # Цвета возможных чисел
		'image_color' :           '#ffffff', # Цвет основного изображения
		'block_color' :           '#f2f2f2', # Цвет нечётных блоков
		'grid_color'  :           '#000000', # Цвет сетки
		'opened_num_color' :      '#000000', # Цвет только что окрытой цифры
		'opened_block_color' :    '#80ff80', # Цвет только что окрытой клетки
		'invalid_color' :         '#ff0000', # Цвет некорректной цифры
		'start_num_color' :       '#000000', # Цвет изначальной цифры
		'filled_num_color' :      '#404040', # Цвет заполненной игроком цифры
		'correct_num_color' :     '#008000', # Цвет правильно заполненной цифры
		'correct_block_color' :   '#80ff80', # Цвет правильно заполненной клетки
		'wrong_num_color' :       '#ff0000', # Цвет неправильно заполненной цифры
		'wrong_block_color' :     '#ff9999', # Цвет неправильно заполненной клетки
		'possible_border_color' : '#000000', # Цвет обводки для возможных чисел

		'grid_type':              'default',
		'highlight':              'rectangle',
		'blocks':                  True,
		'grad':                    False,

		'b_font' : ImageFont.truetype(others + 'arial.ttf', 145), # Шрифт основных чисел
		's_font' : ImageFont.truetype(others + 'arial.ttf', 50),  # Шрифт возможных чисел
		't_font' : ImageFont.truetype(others + 'arial.ttf', 50 + 2 * 2), # Шрифт для обводки возможных чисел

		'title': 'Классическая'
	},
	'dark' : {
		'possible_color' : ['#000000'] + ['#e6e6e6'] * 9,
		'image_color' :           '#1a1a1a', # Цвет основного изображения
		'block_color' :           '#000000', # Цвет нечётных блоков
		'grid_color'  :           '#999999', # Цвет сетки
		'opened_num_color' :      '#000000', # Цвет только что окрытой цифры
		'opened_block_color' :    '#004d00', # Цвет только что окрытой клетки
		'invalid_color' :         '#ff0000', # Цвет некорректной цифры
		'start_num_color' :       '#999999', # Цвет изначальной цифры
		'filled_num_color' :      '#ffffff', # Цвет заполненной игроком цифры
		'correct_num_color' :     '#111111', # Цвет правильно заполненной цифры
		'correct_block_color' :   '#004d00', # Цвет правильно заполненной клетки
		'wrong_num_color' :       '#111111', # Цвет неправильно заполненной цифры
		'wrong_block_color' :     '#990000', # Цвет неправильно заполненной клетки
		'possible_border_color' : '#000000', # Цвет обводки для возможных чисел

		'grid_type':              'default',
		'highlight':              'rectangle',
		'blocks':                  True,
		'grad':                    False,

		'b_font' : ImageFont.truetype(others + 'arial.ttf', 145), # Шрифт основных чисел
		's_font' : ImageFont.truetype(others + 'arial.ttf', 50),  # Шрифт возможных чисел
		't_font' : ImageFont.truetype(others + 'arial.ttf', 50 + 2 * 2), # Шрифт для обводки возможных чисел

		'title': 'Тёмная'
	},
	'fire' : {
		'possible_color' : ['#ffffff'] + ['#000000'] * 9, # Цвета возможных чисел
		'image_color' :           '#ffffff', # Цвет основного изображения
		'block_color' :           '#f2f2f2', # Цвет нечётных блоков
		'grid_color'  :           '#000000', # Цвет сетки
		'opened_num_color' :      '#000000', # Цвет только что окрытой цифры
		'opened_block_color' :    '#008836', # Цвет только что окрытой клетки
		'invalid_color' :         '#ff0000', # Цвет некорректной цифры
		'start_num_color' :       '#000000', # Цвет изначальной цифры
		'filled_num_color' :      '#404040', # Цвет заполненной игроком цифры
		'correct_num_color' :     '#004c00', # Цвет правильно заполненной цифры
		'correct_block_color' :   '#008836', # Цвет правильно заполненной клетки
		'wrong_num_color' :       '#800000', # Цвет неправильно заполненной цифры
		'wrong_block_color' :     '#ff6058', # Цвет неправильно заполненной клетки
		'possible_border_color' : '#000000', # Цвет обводки для возможных чисел

		'grid_type':              'partly',
		'highlight':              'circle',
		'blocks':                  False,

		'grad':                    True,
		'GR_from':                 (255, 255, 0),
		'GR_to':                   (204, 0,   0),
		'grad_padding':            0,
		'grad_square':             2 * im_size, 


		'b_font' : ImageFont.truetype(others + 'arial.ttf', 145), # Шрифт основных чисел
		's_font' : ImageFont.truetype(others + 'arial.ttf', 50),  # Шрифт возможных чисел
		't_font' : ImageFont.truetype(others + 'arial.ttf', 50 + 2 * 2), # Шрифт для обводки возможных чисел

		'title': 'Огненная'
	},
	'sea' : {
		'possible_color' : ['#ffffff'] + ['#000000'] * 9, # Цвета возможных чисел
		'image_color' :           '#ffffff', # Цвет основного изображения
		'block_color' :           '#f2f2f2', # Цвет нечётных блоков
		'grid_color'  :           '#000000', # Цвет сетки
		'opened_num_color' :      '#000000', # Цвет только что окрытой цифры
		'opened_block_color' :    '#008836', # Цвет только что окрытой клетки
		'invalid_color' :         '#ff0000', # Цвет некорректной цифры
		'start_num_color' :       '#000000', # Цвет изначальной цифры
		'filled_num_color' :      '#404040', # Цвет заполненной игроком цифры
		'correct_num_color' :     '#d9d9d9', # Цвет правильно заполненной цифры
		'correct_block_color' :   '#007038', # Цвет правильно заполненной клетки
		'wrong_num_color' :       '#d9d9d9', # Цвет неправильно заполненной цифры
		'wrong_block_color' :     '#900000', # Цвет неправильно заполненной клетки
		'possible_border_color' : '#000000', # Цвет обводки для возможных чисел

		'grid_type':              'partly',
		'highlight':              'circle',
		'blocks':                  False,

		'grad':                    True,
		'GR_from':                 (255, 255, 255),#(255, 255, 0),
		'GR_to':                   (0, 115, 230),#(204, 0,   0),
		'grad_padding':            im_size // 2,
		'grad_square':             3 * im_size // 2, 


		'b_font' : ImageFont.truetype(others + 'arial.ttf', 145), # Шрифт основных чисел
		's_font' : ImageFont.truetype(others + 'arial.ttf', 50),  # Шрифт возможных чисел
		't_font' : ImageFont.truetype(others + 'arial.ttf', 50 + 2 * 2), # Шрифт для обводки возможных чисел

		'title': 'Морская'
	}
}


def gradient(start_color, end_color, start=0, square=2 * im_size):
	def interpolate(f_co, t_co, interval):
		delta =[(t - f) / interval for f , t in zip(f_co, t_co)]
		return [[round(f + det * i) for f, det in zip(f_co, delta)] for i in range(interval)]

	image = Image.new('RGB', (im_size, im_size), 'white')
	draw = ImageDraw.Draw(image)

	for i, color in enumerate(interpolate(start_color, end_color, square)):
		draw.line([(i + start, 0), (0, i + start)], tuple(color), width=1)

	return image


def draw_highlight(x, y, theme, color, image):
	drawer = ImageDraw.Draw(image)
	if theme['highlight'] == 'rectangle':
		drawer.rectangle(R(x, y), fill=color)
	if theme['highlight'] == 'circle':
		drawer.ellipse(C(x, y), fill=color)


def fill_possible(theme, x0: int, y0: int, possible: list, image):
	drawer = ImageDraw.Draw(image)
	for i in range(3):
		for j in range(3):
			x = x0 + j * pos_width + 40
			y = y0 + i * pos_width + 28
			num = possible[i][j]

			if num != 0:
				drawer.text((x - 2, y - 2), str(num), font=theme['t_font'], fill=theme['possible_border_color'])
				drawer.text((x, y),         str(num), font=theme['s_font'], fill=theme['possible_color'][num])


def color_blocks(theme, image, reverse=False):
	drawer = ImageDraw.Draw(image)
	if not reverse:
		drawer.rectangle([(0, 0),                             (im_size / 3, im_size / 3)],        fill=theme['block_color'])
		drawer.rectangle([(im_size / 3, im_size / 3),         (2 * im_size / 3, 2 *im_size / 3)], fill=theme['block_color'])
		drawer.rectangle([(2 * im_size / 3, 2 * im_size / 3), (im_size, im_size)],                fill=theme['block_color'])
		drawer.rectangle([(2 * im_size / 3, 0),               (im_size, im_size / 3)],            fill=theme['block_color'])
		drawer.rectangle([(0, 2 * im_size / 3),               (im_size / 3, im_size)],            fill=theme['block_color'])
	else:
		drawer.rectangle([(im_size / 3, 0),                   (2 * im_size / 3, im_size / 3)],    fill=theme['block_color'])
		drawer.rectangle([(0, im_size / 3),                   (im_size / 3, 2 * im_size / 3)],    fill=theme['block_color'])
		drawer.rectangle([(2 * im_size / 3, im_size / 3),     (im_size, 2 * im_size / 3)],        fill=theme['block_color'])
		drawer.rectangle([(im_size / 3, 2 * im_size / 3),     (2 * im_size / 3, im_size)],        fill=theme['block_color'])


def fill_grid(theme, image):
	drawer = ImageDraw.Draw(image)
	for i in range(10):
		x = 8 + X(i)

		if i % 3:
			drawer.line([(x, 0), (x, im_size)], fill=theme['grid_color'], width=s_border)
			drawer.line([(0, x), (im_size, x)], fill=theme['grid_color'], width=s_border)
		else:
			drawer.line([(x, 0), (x, im_size)], fill=theme['grid_color'], width=b_border)
			drawer.line([(0, x), (im_size, x)], fill=theme['grid_color'], width=b_border)


def fill_partly_grid(theme, image):
	drawer = ImageDraw.Draw(image)
	partly_pad = 20
	for i in range(10):
		x = X(i) + b_border // 2

		if i % 3:
			for j in range(9):
				drawer.line([(x, X(j) + 2 * partly_pad), (x, X(j + 1) - partly_pad)], fill=theme['grid_color'], width=s_border)
				drawer.line([(X(j) + 2 * partly_pad, x), (X(j + 1) - partly_pad, x)], fill=theme['grid_color'], width=s_border)
		else:
			if i != 0 and i != 9:
				drawer.line([(x, 0), (x, im_size)], fill=theme['grid_color'], width=b_border)
				drawer.line([(0, x), (im_size, x)], fill=theme['grid_color'], width=b_border)


def fill_ivalid(theme, puzzle: list, current: list, image):
	drawer = ImageDraw.Draw(image)
	for i in range(9):
		for j in range(9):
			if current[i][j] == 0:
				continue
			x, y = X(j), Y(i)

			for k in range(9):
				if current[i][k] == current[i][j] and k != j:
					if current[i][j] != puzzle[i][j]:
						draw_highlight(x, y, theme=theme, color=theme['invalid_color'], image=image)
					if current[i][k] != puzzle[i][k]:
						draw_highlight(X(k), y, theme=theme, color=theme['invalid_color'], image=image)
				if current[k][j] == current[i][j] and k != i:
					if current[i][j] != puzzle[i][j]:
						draw_highlight(x, y, theme=theme, color=theme['invalid_color'], image=image)
					if current[k][j] != puzzle[k][j]:
						draw_highlight(x, Y(k), theme=theme, color=theme['invalid_color'], image=image)

			row = 3 * (i // 3)
			col = 3 * (j // 3)
			for r in range(row, row + 3):
				for c in range(col, col + 3):
					if current[r][c] == current[i][j] and (r != i or c != j):
						if current[i][j] != puzzle[i][j]:
							draw_highlight(x, y, theme=theme, color=theme['invalid_color'], image=image)
						if current[r][c] != puzzle[r][c]:
							draw_highlight(X(c), Y(r), theme=theme, color=theme['invalid_color'], image=image)


def fill_numbers(theme, puzzle: list, current: list, solution: list, image, opened: tuple=None):
	drawer = ImageDraw.Draw(image)
	for i in range(9):
		for j in range(9):
			x, y = X(j), Y(i)

			if (i, j) == opened:
				draw_highlight(x, y, theme=theme, color=theme['opened_block_color'], image=image)
				drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=theme['b_font'], fill=theme['opened_num_color'])
			elif puzzle[i][j] != 0:
				drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(puzzle[i][j]), font=theme['b_font'], fill=theme['start_num_color'])
			elif puzzle[i][j] == 0 and current[i][j] != 0:
				if not solution:
					drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=theme['b_font'], fill=theme['filled_num_color'])
				elif current[i][j] == solution[i][j]:
					draw_highlight(x, y, theme=theme, color=theme['correct_block_color'], image=image)
					drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=theme['b_font'], fill=theme['correct_num_color'])
				elif current[i][j] != 0:
					draw_highlight(x, y, theme=theme, color=theme['wrong_block_color'], image=image)
					drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=theme['b_font'], fill=theme['wrong_num_color'])
				else:
					pass


def fill_all_possible(theme, puzzle: list, current: list, image):
	drawer = ImageDraw.Draw(image)
	for i in range(9):
		for j in range(9):
			x, y = X(j), Y(i)

			if puzzle[i][j] == 0 and current[i][j] == 0:
				fill_possible(theme, x, y, sudoku.get_block_possible(i, j, current), image)


def draw_sudoku(puzzle: list=None, current: list=None, solution: list=None, grid=True, possible: bool=False, correct: bool=False, invalid: bool=False, solved: bool=False, opened: tuple=None, theme='sea'):
	theme = THEMES[theme]
	if theme['grad']:
		image = gradient(theme['GR_from'], theme['GR_to'], theme['grad_padding'], theme['grad_square'])
	else:
		image = Image.new('RGB', (im_size, im_size), theme['image_color'])

	if theme['blocks']:
		color_blocks(theme, image=image)
	if invalid:
		fill_ivalid(theme, puzzle=puzzle, current=current, image=image)
	if possible:
		fill_all_possible(theme, puzzle=puzzle, current=current, image=image)
	if solved:
		fill_numbers(theme, puzzle=puzzle, current=solution, solution=None, image=image, opened=opened)
	elif correct:
		fill_numbers(theme, puzzle=puzzle, current=current, solution=solution, image=image, opened=opened)
	else:
		fill_numbers(theme, puzzle=puzzle, current=current, solution=None, image=image, opened=opened)
	if grid:
		if theme['grid_type'] == 'partly':
			fill_partly_grid(theme, image=image)
		else:
			fill_grid(theme, image=image)

	#image.show()
	image.save(others + 'sudoku.jpg')


#puzzle   = decompressPuzzle('203000601070000000008002040040070000300000574050000020700910050004208030000740000')
#current  = decompressPuzzle('293333681475186000168392745942571863381629574657000129726913458514268930000745215')
#solution = decompressPuzzle('293457681475186392168392745942571863381629574657834129726913458514268937839745216')

#draw_sudoku(puzzle=puzzle, current=current, solution=solution, correct=True)
# python C:\Users\HP_650\Desktop\Python_BOT\field.py

if __name__ != '__main__':
	print('Модуль отрисовки судоку подключен и работает исправно')
