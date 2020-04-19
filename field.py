from PIL import Image, ImageDraw, ImageFont
from database import others
from random import randint
import sudoku
import copy


possible_color = ['white', '#ff0003', '#ff8a00', '#fff000', '#7dff00', '#00c000', '#00fbf3', '#2447ff', '#000297', '#4e006c']
block_color =           '#f2f2f2'
grid_color  =           '#000000'
start_num_color =       '#000000'
filled_num_color =      '#404040'
correct_num_color =     '#008000'
wrong_num_color =       '#ff0000'
possible_border_color = '#000000'
image_color =           '#ffffff'

b_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', 145)
s_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', 50)
t_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', 50 + 2 * 2)

b_border = 18
s_border = 8
width = 200
im_size = width * 9 + s_border * 6 + b_border * 4
pos_width = 60

X = lambda x: b_border * (x // 3) + s_border * (x - x // 3) + x * width
Y = lambda y: b_border * (y // 3) + s_border * (y - y // 3) + y * width
R = lambda x, y: [(x + s_border, y + s_border), (x + b_border + width, y + b_border + width)] 

def fill_possible(x0: int, y0: int, possible: list, image):
	drawer = ImageDraw.Draw(image)
	for i in range(3):
		for j in range(3):
			x = x0 + j * pos_width + 40
			y = y0 + i * pos_width + 28
			num = possible[i][j]

			if num != 0:
				drawer.text((x - 2, y - 2), str(num), font=t_font, fill=possible_border_color)
				drawer.text((x, y), str(num), font=s_font, fill=possible_color[num])


def color_blocks(image, reverse=False):
	drawer = ImageDraw.Draw(image)
	if not reverse:
		drawer.rectangle([(0, 0), (im_size / 3, im_size / 3)], fill=block_color)
		drawer.rectangle([(im_size / 3, im_size / 3), (2 * im_size / 3, 2 *im_size / 3)], fill=block_color)
		drawer.rectangle([(2 * im_size / 3, 2 * im_size / 3), (im_size, im_size)], fill=block_color)
		drawer.rectangle([(2 * im_size / 3, 0), (im_size, im_size / 3)], fill=block_color)
		drawer.rectangle([(0, 2 * im_size / 3), (im_size / 3, im_size)], fill=block_color)
	else:
		drawer.rectangle([(im_size / 3, 0), (2 * im_size / 3, im_size / 3)], fill=block_color)
		drawer.rectangle([(0, im_size / 3), (im_size / 3, 2 * im_size / 3)], fill=block_color)
		drawer.rectangle([(2 * im_size / 3, im_size / 3), (im_size, 2 * im_size / 3)], fill=block_color)
		drawer.rectangle([(im_size / 3, 2 * im_size / 3), (2 * im_size / 3, im_size)], fill=block_color)
	


def fill_grid(image):
	drawer = ImageDraw.Draw(image)
	for i in range(10):
		x = 8 + X(i)

		if i % 3:
			drawer.line([(x, 0), (x, im_size)], fill=grid_color, width=s_border)
			drawer.line([(0, x), (im_size, x)], fill=grid_color, width=s_border)
		else:
			drawer.line([(x, 0), (x, im_size)], fill=grid_color, width=b_border)
			drawer.line([(0, x), (im_size, x)], fill=grid_color, width=b_border)


def fill_numbers(puzzle: list, current: list, solution: list, image):
	drawer = ImageDraw.Draw(image)
	for i in range(9):
		for j in range(9):
			x, y = X(j), Y(i)

			if puzzle[i][j] != 0:
				drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(puzzle[i][j]), font=b_font, fill=start_num_color)
			elif puzzle[i][j] == 0 and current[i][j] != 0:
				if not solution:
					drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=b_font, fill=filled_num_color)
				elif current[i][j] == solution[i][j]:
					drawer.rectangle(R(x, y), fill='#80ff80')
					drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=b_font, fill='#000000')
				elif current[i][j] != 0:
					drawer.rectangle(R(x, y), fill='#ff9999')
					drawer.text((width // 4 + 23 + x, width // 16 + 23 + y), str(current[i][j]), font=b_font, fill='#000000')
				else:
					pass


def fill_all_possible(puzzle: list, current: list, image):
	drawer = ImageDraw.Draw(image)
	for i in range(9):
		for j in range(9):
			x, y = X(j), Y(i)

			if puzzle[i][j] == 0 and current[i][j] == 0:
				fill_possible(x, y, sudoku.get_block_possible(i, j, current), image)


def draw_sudoku_possible(puzzle: list, current: list):
	image = Image.new('RGB', (im_size, im_size), image_color)

	color_blocks(image)
	fill_grid(image)
	fill_numbers(puzzle, current, None, image)
	fill_all_possible(puzzle, current, image)

	#image.show()
	image.save(others + 'possible.jpg')


def draw_sudoku_correct(puzzle: list, current: list, solution: list):
	image = Image.new('RGB', (im_size, im_size), image_color)

	color_blocks(image)
	fill_numbers(puzzle, current, solution, image)
	fill_grid(image)

	#image.show()	
	image.save(others + 'correct.jpg')


def draw_sudoku(puzzle: list, current: list):
	image = Image.new('RGB', (im_size, im_size), image_color)

	color_blocks(image)
	fill_grid(image)
	fill_numbers(puzzle, current, None, image)

	#image.show()	
	image.save(others + 'sudoku.jpg')


def draw_sudoku_solution(puzzle: list, solution: list):
	image = Image.new('RGB', (im_size, im_size), image_color)

	color_blocks(image)
	fill_grid(image)
	fill_numbers(puzzle, solution, None, image)

	#image.show()
	image.save(others + 'solution.jpg')


#python C:\Users\HP_650\Desktop\Python_BOT\field.py

if __name__ != '__main__':
	print('Модуль отрисовки судоку подключен и работает исправно')
