import telebot
from telebot import types
import datetime
import database
import graphic
import sudoku
import field
import math
import re
import AI

PRIZE = ['🥇', '🥈', '🥉']
GROW = ['📈', '⏺', '📉']
SOLVED = ['❌', '✅']
NUM = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
TOKEN = "1099904106:AAH0rNHEL-7T15gllpGzpqXr-Ewgdo9UuXc"
bot = telebot.TeleBot(TOKEN)


def get_prize(i: int) -> str:
	if i < len(PRIZE):
		return PRIZE[i]
	else:
		return '      ' * len(PRIZE[0])


def get_grow(grow: float) -> str:
	if grow > 0.0:
		return GROW[0]
	elif grow < 0.0:
		return GROW[2]
	else:
		return GROW[1]


def sign(num: float) -> str:
	if (num < 0):
		return str(num)
	elif (num > 0):
		return '+' + str(num)
	else:
		return ' ' + str(num)


def convert_to_emoji(solution, size = 9):
	ans = ''
	for i in range(size):
		for j in range(size):
			if solution[i][j] == 0:
				ans += "✖️"
			else:
				ans += NUM[solution[i][j]]
			if not (j + 1) % 3:
				ans += "    "
		ans += '\n'
		if not (i + 1) % 3:
			ans += '\n'
	return ans


def checkTextMessage(message):
	temp = message.text.replace(' ', '').split('\n')

	while '' in temp:
		temp.remove('')

	if len(temp) != 9:
		return "Строк судоку должно быть ровно 9 строк"

	for i in range(9):
		temp[i] = temp[i][1:-1].split(',')
		if len(temp[i]) != 9:
			return "В каждой строке судоку должно быть ровно 9 чисел"
	
	puzzle = []
	for i in range(9):
		puzzle.append([])
		for j in range(9):
			temp[i][j] = temp[i][j].strip()
			if not temp[i][j].isnumeric():
				return "Все элементы должны быть числами"
			if int(temp[i][j]) < 0 or int(temp[i][j]) > 9:
				return "Все элементы должны быть числами в интервале от 0 до 9"
			puzzle[i].append(int(temp[i][j]))
	return puzzle


def checkEmojiMessage(message):
	temp = message.text.replace("✖️", NUM[0]).split('\n')
	while '' in temp:
		temp.remove('')

	if len(temp) != 9:
		return "Строк судоку должно быть ровно 9 строк"

	for i in range(9):
		temp[i] = ''.join(filter(lambda x: x.isdigit(), temp[i]))
		if len(temp[i]) != 9:
			return "В каждой строке судоку должно быть ровно 9 чисел от 1 до 9"

	puzzle = []
	for i in range(9):
		puzzle.append([])
		for j in range(9):
			if not temp[i][j].isnumeric():
				return "Все элементы должны быть числами"
			if int(temp[i][j]) < 0 or int(temp[i][j]) > 9:
				return "Все элементы должны быть числами в интервале от 0 до 9"
			puzzle[i].append(int(temp[i][j]))
	return puzzle
	

@bot.message_handler(commands=['start', 'reg'])
def start(message):
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Похоже, что у вас не задан username (имя пользователя вида @User). Пока username не задан, я не могу зарегестрировать вас в базе данных.')
		return
	username = '@' + message.from_user.username

	if database.isUserExist(username):
		bot.send_message(message.chat.id, 'Вы уже зарегестрированы в базе данных')
	else:
		bot.send_message(message.chat.id, 'Вы еще не зарегестрированы в системе, процесс регистрации может занять некотрое время')
		database.addUser(message.chat.id, username)
		bot.send_message(message.chat.id, 'Ок, теперь вы зарегестрированы в базе данных')


@bot.message_handler(commands=['unreg'])
def unreg(message):
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Похоже, что у вас не задан username (имя пользователя вида @User). Пока username не задан, я не могу зарегестрировать вас в базе данных.')
		return
	username = '@' + message.from_user.username

	if not database.isUserExist(username):
		bot.send_message(message.chat.id, 'Вы ещё не зарегестрированы в базе данных')
	else:
		bot.send_message(message.chat.id, 'Вы действительно хотите удалить свой профиль из базы данных? (да\\нет)')
		bot.register_next_step_handler(message, delete_profile)


def delete_profile(message):
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Похоже, что у вас не задан username (имя пользователя вида @User). Пока username не задан, я не могу зарегестрировать вас в базе данных.')
		return
	username = '@' + message.from_user.username
	if message.text.lower() == 'да':
		database.deleteUser(username)
		bot.send_message(message.chat.id, 'Ваш профиль был успешно удалён.')


@bot.message_handler(commands=['methods'])
def methods(message):
	if validate(message):
		bot.send_message(message.chat.id, database.get_methods_list())


@bot.message_handler(commands=['last_hero', 'last_hero_line', 'no_choise', 'who_if_not_me', 'naked_pairs', 'threesome', 'great_four', 'hidden_three', 'hidden_four'])
def send_method_with_1_example(message):
	if not validate(message):
		return
	method_name = message.text
	bot.send_message(message.chat.id, database.get_method_description(method_name))
	photo = open(database.method + method_name + '\\' + 'example.png', 'rb')
	bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['hidden_pairs', 'indicating_combs', 'reduce_irreducible'])
def send_method_with_2_example(message):
	if not validate(message):
		return
	method_name = message.text
	for i in range(1, 3):
		bot.send_message(message.chat.id, database.get_method_description(method_name, '_' + str(i)))
		photo = open(database.method + method_name + '\\' + 'example' + '_' + str(i) + '.png', 'rb')
		bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['level_raiting'])
def level_raiting(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	raiting = database.level_rating()
	table = ""

	for i, user in enumerate(raiting):
		if (i < 10 or user[0] == username):
			table += '{:>2}{}{:>7.3f} {}\n' . format(str(i + 1) + '.', get_prize(i), user[1], user[0])

	bot.send_message(message.chat.id, table)


@bot.message_handler(commands=['score_raiting'])
def score_raiting(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	raiting = database.score_rating()
	max_score = len(str(raiting[0][1]))
	table = ""

	for i, user in enumerate(raiting):
		if (i < 10 or user[0] == username):
			table += '{:>2}{}{} {}\n' . format(str(i + 1) + '.', get_prize(i), str(user[1]).rjust(max_score + 1, '.').replace('.', '  '), user[0])

	bot.send_message(message.chat.id, table)


@bot.message_handler(commands=['records'])
def score_raiting(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	records = database.records_list()
	table = ""

	for record in records:
		table += '{:>2}:  {}  -  {}\n' . format(record[0], record[1], record[2])

	bot.send_message(message.chat.id, table)


@bot.message_handler(commands=['level_graphics'])
def level_graphics(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if len(database.getUserHistory(username)) < 5:
		bot.send_message(message.chat.id, 'Вы ещё не сыграли достаточно раз')
	else:
		graphic.get_graphic(username)
		photo = open(database.others + 'HISTORY.png', 'rb')
		bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['history'])
def history(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	history = database.getUserHistory(username)
	table = ''

	if history != ['']:
		for row in history:
			row = row.split(' ')
			table += '{}{} {:<5.2f}  {}  {}\n' . format(SOLVED[int(row[0])], get_grow(float(row[3])), float(row[1]), row[2], sign(float(row[3])).ljust(5))
		bot.send_message(message.chat.id, table)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не играли')


@bot.message_handler(commands=['my_score'])
def my_score(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	bot.send_message(message.chat.id, f'Ваш текущий счёт = {format(database.getUserScore(username))}')


@bot.message_handler(commands=['my_level'])
def my_level(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	bot.send_message(message.chat.id, 'Ваш текущий уровень = ' + str('{:.2f}' . format(database.getUserLevel(username))))


@bot.message_handler(commands=['my_rank'])
def my_rank(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	bot.send_message(message.chat.id, 'Ваш текущий ранг = ' + str(sudoku.getRank(round(database.getUserLevel(username)))))


@bot.message_handler(commands=['challenge_mode'])
def challenge_mode(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.getGamemode(username) != 'challenge':
		database.setGamemode('challenge', username)
		bot.send_message(message.chat.id, 'Теперь вы играете в режиме challenge, это подразумевает, что после комманды /next_sudoku пойдёт отсчет времени и в зависимости от того, как быстро вы решите судоку, ваш уровень будет расти или понижаться')
		database.resetUserTime(username)
	else:
		bot.send_message(message.chat.id, 'Вы уже играете в режиме challenge')


@bot.message_handler(commands=['freeplay_mode'])
def freeplay_mode(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.getGamemode(username) == 'challenge' and database.isUserPlay(username):
		bot.send_message(message.chat.id, 'Вы ещё не закончили сборку прошлой головоломки, если хотите сдаться, то нажмите /give_up (ваш уровень будет понижен)')
	elif database.getGamemode(username) != 'freeplay':
		database.setGamemode('freeplay', username)
		bot.send_message(message.chat.id, 'Теперь вы играете в режиме freeplay, это подразумевает, что после комманды /next_sudoku отсчёта времени не последует, а ваш уровень не будет расти или понижаться')
	else:
		bot.send_message(message.chat.id, 'Вы уже играете в режиме freeplay')


@bot.message_handler(commands=['open_cell'])
def open_cell(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		bot.send_message(message.chat.id, 'Для того, чтобы открыть любую пустую клетку в изначальном судоку вам необходимо ввести два числа в формате (строка столбец).')
		bot.register_next_step_handler(message, parse_cell)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


def parse_cell(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	pattern = re.compile(r'[({][1-9].[1-9][})]')

	print(message.text)
	if not pattern.match(message.text):
		bot.send_message(message.chat.id, 'Неверный формат координат клетки, необходимо ввести координаты в формате (строка столбец). Можете попробовать ещё /open_cell')
	elif database.getUserPuzzle(username)[int(message.text[1]) - 1][int(message.text[-2]) - 1] != 0:
		bot.send_message(message.chat.id, 'Эта клетка не пустая. Можете попробовать ещё /open_cell')
	elif database.isUserPlay(username):
		database.updateUserPuzzle(int(message.text[1]) - 1, int(message.text[-2]) - 1, username)
		field.draw_sudoku(database.getUserPuzzle(username), database.getUserCurrent(username))
		photo = open(database.others + 'sudoku.jpg', 'rb')
		AI.cell_penalty(username)
		bot.send_photo(message.chat.id, photo)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['check_correctness'])
def check_correctness(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		field.draw_sudoku_correct(database.getUserPuzzle(username), database.getUserCurrent(username), database.getUserSolution(username))
		photo = open(database.others + 'correct.jpg', 'rb')
		AI.check_penalty(username)
		bot.send_photo(message.chat.id, photo)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['get_tip'])
def get_tip(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		penalty_cell = AI.avg_time(database.getUserLevel(username)) * AI.cell_penalty_koef * 60
		penalty_check = AI.avg_time(database.getUserLevel(username)) * AI.check_penalty_koef * 60
		bot.send_message(message.chat.id, f'Выберите интересующую вас подсказку из доступных ниже. Обратите внимание на то, что за разные подсказки могут накладываться различные штрафы ко времени решения.\n\n/check_correctness  +{penalty_check:.0f} секунд ко времени решения\n/open_cell +{penalty_cell:.0f} секунд ко времени решения')
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['possible'])
def possible(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		field.draw_sudoku_possible(database.getUserPuzzle(username), database.getUserCurrent(username))
		photo = open(database.others + 'possible.jpg', 'rb')
		bot.send_photo(message.chat.id, photo)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['give_up'])
def give_up(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.getGamemode(username) == 'freeplay':
		bot.send_message(message.chat.id, 'Вы играете в режиме freeplay, сдаваться смысла нет')
	elif database.isUserPlay(username):
		AI.recount_level(username, True)
		bot.send_message(message.chat.id, 'Вы сдались, ваш уровень был понижен (текущий уровень /my_level)')
		database.resetUserTime(username)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['current_text'])
def current_text(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		bot.send_message(message.chat.id, sudoku.getStrPuzzle(database.getUserCurrent(username)))
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['current_emoji'])
def current_emoji(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		bot.send_message(message.chat.id, convert_to_emoji(database.getUserCurrent(username)))
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['current_photo'])
def current_photo(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		field.draw_sudoku(database.getUserPuzzle(username), database.getUserCurrent(username))
		photo = open(database.others + 'sudoku.jpg', 'rb')
		bot.send_photo(message.chat.id, photo)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['current_sudoku'])
def current_sudoku(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		bot.send_message(message.chat.id, 'Выберите подходящий вам формат:\n\n/current_text - текстовый\n/current_emoji - в виде эмодзи\n/current_photo - в виде фото')
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['initial_text'])
def initial_text(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		bot.send_message(message.chat.id, sudoku.getStrPuzzle(database.getUserPuzzle(username)))
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['initial_emoji'])
def initial_emoji(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		bot.send_message(message.chat.id, convert_to_emoji(database.getUserPuzzle(username)))
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['initial_photo'])
def initial_photo(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		field.draw_sudoku(database.getUserPuzzle(username), database.getUserPuzzle(username))
		photo = open(database.others + 'sudoku.jpg', 'rb')
		bot.send_photo(message.chat.id, photo)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['initial_sudoku'])
def initial_sudoku(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		bot.send_message(message.chat.id, 'Выберите подходящий вам формат:\n\n/initial_text - текстовый\n/initial_emoji - в виде эмодзи\n/initial_photo - в виде фото')
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['next_sudoku'])
def next_sudoku(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username) and database.getGamemode(username) != 'freeplay':
		bot.send_message(message.chat.id, 'Вы ещё не закончили сборку прошлой головоломки, если хотите сдаться, то нажмите /give_up (ваш уровень будет понижен)')
	else:
		database.nextPuzzle(username)
		database.setUserTime(datetime.datetime.today(), username)
		initial_photo(message)


@bot.message_handler(content_types=['text'])
def answerTheMessage(message):
	if not validate(message):
		return

	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		puzzle_1 = checkTextMessage(message)
		puzzle_2 = checkEmojiMessage(message)
		puzzle = None

		if type(puzzle_1) is str and type(puzzle_2) is str:
			bot.reply_to(message, puzzle_1)
			return
		elif type(puzzle_1) is not str:
			puzzle = puzzle_1
		else:
			puzzle = puzzle_2


		if not sudoku.are_equal(puzzle, database.getUserPuzzle(username)):
			bot.send_message(message.chat.id, 'Вы прислали не то судоку')
		elif not sudoku.isCorrect(puzzle):
			bot.send_message(message.chat.id, 'Судоку заполнено с ошибками (повтор с блоке/строке/столбце)')
		elif not sudoku.isSolved(puzzle):
			database.setUserCurrent(puzzle, username)
			bot.send_message(message.chat.id, 'Вы заполнили не все пустые клетки')
		elif True or database.isCorrectSolution(puzzle, username):
			database.setUserCurrent(puzzle, username)
			current_photo(message)

			diff = database.getUserLevel(username)
			time = database.solvingTime(username)

			if database.is_new_record(time, diff):
				prev = database.get_record(diff)
				bot.send_message(message.chat.id, f'Вы установили новый рекорд!\nПредыдущий рекорд:\n{prev[0]} - {prev[1]}')
				database.update_record(time, diff, username)

			AI.recount_level(username)

			time = database.convert(time)
			bot.send_message(message.chat.id, 'Поздравляю, вы правильно решили судоку за {}.\nДля начала решения следующей головоломки нажмите /next_sudoku' . format(time))
			database.resetUserTime(username)
		else:
			bot.send_message(message.chat.id, 'Увы, но решение неправильное')
	else:
		bot.send_message(message.chat.id, 'Вы пока не начали игру, для начала игры нажмите /next_sudoku')


def validate(message) -> bool:
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Похоже, что у вас не задан username (имя пользователя вида @User). Пока username не задан, я не могу зарегестрировать вас в базе данных.')
		return False
	elif not database.isUserExist('@' + message.from_user.username):
		bot.send_message(message.chat.id, 'Вы пока не зарегестрированы, возможно произошёл сбой. Для регистрации нажмите /start')
		return False
	else:
		database.udateLastUserActivity('@' + message.from_user.username)
		return True


for user in database.unactive_users(14):
	try:
		bot.send_message(database.getID(user), 'От вас за последние 14 дней не было никакой активности, мне пришлось удалить вас из базы дынных')
	except telebot.apihelper.ApiException:
		pass
	database.deleteUser(user)
for user in database.unactive_users(2):
	if database.isUserPlay(user):
		AI.recount_level(user, True)
	database.resetUserTime(user)
	if (datetime.datetime.today() - database.getLastUserAlert(user)).days >= 2:
		delta = datetime.datetime.today() - database.getLastUserActivity(user)
		print(f'{user} {delta}')
		try:
			bot.send_message(database.getID(user), f'От вас за последние {delta.days} дней и {delta.seconds // 3600} часа(ов) не было никакой активности.') 
			bot.send_message(database.getID(user), 'По истечению 14 суток мне прийдется удалить вас и все ваши игровые достижения из базы данных. Если вы хотите отключить напоминания, вы можете самостоятельно выйти из игры с потерей всех данных при помощи комманды /unreg')
		except telebot.apihelper.ApiException:
			database.deleteUser(user)
		else:
			database.udateLastUserAlert(user)

bot.polling(none_stop = True, interval = 0)
#python C:\Users\HP_650\Desktop\Python_BOT\bot.py
