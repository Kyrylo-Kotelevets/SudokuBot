from _thread import start_new_thread
from telebot import types
from time import sleep
import telebot
import datetime
import database
import graphic
import sudoku
import backup
import field
import math
import AI

PRIZE = ['🥇', '🥈', '🥉']
GROW = ['📈', '⏺', '📉']
SOLVED = ['❌', '✅']
NUM = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
TOKEN = '1142618827:AAFWbpi1aXGGVb8wFMAbSUFDm9BWhWj6AQU'
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
		bot.send_message(message.chat.id, 'Вы еще не зарегестрированы в базе данных, ожидайте, процесс регистрации может занять несколько минут')
		database.addUser(message.chat.id, username)
		bot.send_message(message.chat.id, 'Ок, теперь вы зарегестрированы в базе данных')
		menu(message)


@bot.message_handler(commands=['unreg'])
def unreg(message):
	if validate(message):
		keyboard = telebot.types.ReplyKeyboardMarkup(True)
		keyboard.row('Да', 'Нет')
		bot.send_message(message.chat.id, 'Вы действительно хотите удалить свой профиль из базы данных?', reply_markup=keyboard)
		bot.register_next_step_handler(message, delete_profile)


@bot.message_handler(commands=['recovery'])
def recovery(message):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Мой пароль', callback_data='password'))
		bot.send_message(message.chat.id, 'Для восстановления аккаунта вам необходимо прислать мне сообщение вида \'@username password\', где username - никнейм аккаунта, котрый вы хотите восстановить, а password - соответсвенный пароль.', reply_markup=markup)


@bot.message_handler(commands=['password'])
def password(message):
	if validate(message):
		username = '@' + message.from_user.username
		database.updatePassword(username)
		bot.send_message(message.chat.id, 'Ваш текущий пароль: {}\nНе сообщайте его никому!' . format(database.getPassword(username)))


@bot.message_handler(commands=['menu'])
def menu(message):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		if database.isUserPlay('@' + message.from_user.username):
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Продолжить игру', callback_data='current_photo'))
		else:
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Начать игру', callback_data='next_sudoku'))
		markup.add(telebot.types.InlineKeyboardButton(text='📚 Методы решения', callback_data='methods'))
		markup.add(telebot.types.InlineKeyboardButton(text='📆 История решений', callback_data='history'))
		if database.getUserCount('@' + message.from_user.username)[0] >= 5:
			markup.add(telebot.types.InlineKeyboardButton(text='📉 График изменения уровня', callback_data='level_graphics'))
		markup.add(telebot.types.InlineKeyboardButton(text='🕹 Сменить режим игры', callback_data='change_mode'))
		markup.add(telebot.types.InlineKeyboardButton(text='Сменить тему', callback_data='change_theme'))
		markup.add(telebot.types.InlineKeyboardButton(text='🏋 Мой уровень', callback_data='my_level'))
		markup.add(telebot.types.InlineKeyboardButton(text='🎗 Мой ранг', callback_data='my_rank'))
		markup.add(telebot.types.InlineKeyboardButton(text='💯 Мой счёт', callback_data='my_score'))
		markup.add(telebot.types.InlineKeyboardButton(text='🏅 Рейтинги', callback_data='raitings'))
		markup.add(telebot.types.InlineKeyboardButton(text='🏆 Рекорды', callback_data='records'))
		markup.add(telebot.types.InlineKeyboardButton(text='📊 Статистика', callback_data='stats'))
		markup.add(telebot.types.InlineKeyboardButton(text='❓ Помощь', callback_data='help'))
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, 'Можете выбрать интересующий вас пункт из меню либо воспользаваться коммандами из списка', reply_markup=markup)


@bot.message_handler(commands=['raitings'])
def raitings(message, back_menu = False):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='📊 Процент успешности', callback_data='success_raiting'), telebot.types.InlineKeyboardButton(text='✅ Решенные судоку', callback_data='count_raiting'))
		markup.add(telebot.types.InlineKeyboardButton(text='🏋 Уровень', callback_data='level_raiting'), telebot.types.InlineKeyboardButton(text='💯 Очки', callback_data='score_raiting'))
		if back_menu:
			markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_menu'))
		bot.send_message(message.chat.id, 'Доступно несколько парматеров для сортировки игроков, выберите один из них:', reply_markup=markup)


@bot.message_handler(commands=['authors'])
def authors(message):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_help'))
		bot.send_message(message.chat.id, 'Проект создан студентом ХНУРЭ кафедры ИИ - @WeNoM_21\nВсе вопросы, технические сбои и отзывы принимаются в ЛС по указанному выше адресу.', reply_markup=markup)


@bot.message_handler(commands=['rules'])
def rules(message):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
		markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_help'))
		bot.send_photo(message.chat.id, open(database.others + 'rules.jpg', 'rb'), database.__read(database.others + 'rules.txt'), reply_markup=markup)


@bot.message_handler(commands=['system'])
def system(message):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
		markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_help'))
		bot.send_message(message.chat.id, database.__read(database.others + 'system.txt'), reply_markup=markup)


@bot.message_handler(commands=['manual'])
def manual(message):
	if validate(message):
		bot.send_message(message.chat.id, database.__read(database.others + 'manual_1.txt'))
		bot.send_media_group(message.chat.id, [types.InputMediaPhoto(open(database.others + photo + '.jpg', 'rb')) for photo in ['manual_text', 'manual_emoji']])

		bot.send_message(message.chat.id, database.__read(database.others + 'manual_2.txt'))
		bot.send_media_group(message.chat.id, [types.InputMediaPhoto(open(database.others + photo + '.jpg', 'rb')) for photo in ['manual_mixed_text', 'manual_mixed_emoji', 'manual_mixed']])

		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku_from_manual'))
		markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_help_from_manual'))
		bot.send_message(message.chat.id, database.__read(database.others + 'manual_3.txt'), reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message, back_menu=True):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Как играть?', callback_data='manual'))
		markup.add(telebot.types.InlineKeyboardButton(text='Правила судоку', callback_data='rules'))
		markup.add(telebot.types.InlineKeyboardButton(text='Cистема оценивания', callback_data='system'))
		markup.add(telebot.types.InlineKeyboardButton(text='Авторы/Поддержка', callback_data='authors'))
		if back_menu:
			markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_menu'))
		bot.send_message(message.chat.id, 'У вас возникли трудности или появились вопросы?\nЕсли да, то выберите вариант из списка ниже:', reply_markup=markup)


def delete_profile(message):
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Похоже, что у вас не задан username (имя пользователя вида @User). Пока username не задан, я не могу зарегестрировать вас в базе данных.')
		return
	username = '@' + message.from_user.username
	if message.text.lower() == 'да':
		database.deleteUser(username)
		bot.send_message(message.chat.id, 'Ваш профиль был успешно удалён.', reply_markup=telebot.types.ReplyKeyboardRemove())
	else:
		bot.send_message(message.chat.id, 'Я рад, что вы пока остаетесь с нами', reply_markup=telebot.types.ReplyKeyboardRemove())	


@bot.message_handler(commands=['stats'])
def stats(message):
	if validate(message):
		username = '@' + message.from_user.username
		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, f'Ваш процент успешности:   {100 * count[0] / max(1, (count[0] + count[1])):.4f}%\n🔢Всего судоку:      {count[0] + count[1]}\n✅Решено судоку:  {count[0]}\n❌Не решено:         {count[1]}', reply_markup=markup)


@bot.message_handler(commands=['methods'])
def methods(message, back_menu=False):
	if validate(message):
		markup = telebot.types.InlineKeyboardMarkup()
		if back_menu:
			markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_menu'))
		else:
			markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, database.get_methods_list(), reply_markup=markup)


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
	if validate(message):
		username = '@' + message.from_user.username

		raiting = database.level_rating()
		table = ''

		for i, user in enumerate(raiting):
			if (i < 10 or user[0] == username):
				table += '{:>2}{}{:>7.3f} {}\n' . format(str(i + 1) + '.', get_prize(i), user[1], user[0])

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, table, reply_markup=markup)


@bot.message_handler(commands=['success_raiting'])
def success_raiting(message):
	if validate(message):
		username = '@' + message.from_user.username

		raiting = database.success_rating()
		table = ''

		for i, user in enumerate(raiting):
			if (i < 10 or user[0] == username):
				table += '{:>2}{}{:>7.4f}% {}\n' . format(str(i + 1) + '.', get_prize(i), user[1], user[0])

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, table, reply_markup=markup)


@bot.message_handler(commands=['count_raiting'])
def count_raiting(message):
	if validate(message):
		username = '@' + message.from_user.username

		raiting = database.count_raiting()
		table = ''

		for i, user in enumerate(raiting):
			if (i < 10 or user[0] == username):
				table += '{:>2}{}{:>4} {}\n' . format(str(i + 1) + '.', get_prize(i), user[1], user[0])

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, table, reply_markup=markup)


@bot.message_handler(commands=['score_raiting'])
def score_raiting(message):
	if validate(message):
		username = '@' + message.from_user.username

		raiting = database.score_rating()
		max_score = len(str(raiting[0][1]))
		table = ""

		for i, user in enumerate(raiting):
			if (i < 10 or user[0] == username):
				table += '{:>2}{}{} {}\n' . format(str(i + 1) + '.', get_prize(i), str(user[1]).rjust(max_score + 1, '.').replace('.', '  '), user[0])

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, table, reply_markup=markup)


@bot.message_handler(commands=['records'])
def records(message):
	if validate(message):
		username = '@' + message.from_user.username

		records = database.records_list()
		table = ""

		for record in records:
			table += '{:>2}:  {}  -  {}\n' . format(record[0], record[1], record[2])

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, table, reply_markup=markup)


@bot.message_handler(commands=['level_graphics'])
def level_graphics(message):
	if validate(message):
		username = '@' + message.from_user.username

		if database.getUserCount(username)[0] < 5:
			bot.send_message(message.chat.id, 'Для того, чтобы я мог отобразить графически изменения вашего уровня, вам необходимо решить как минимум 5 судоку.')
		else:
			graphic.draw(username)
			photo = open(database.others + 'HISTORY.png', 'rb')

			count = database.getUserCount(username)
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
			bot.send_photo(message.chat.id, photo, reply_markup=markup)


@bot.message_handler(commands=['history'])
def history(message):
	if validate(message):
		username = '@' + message.from_user.username

		history = database.getUserHistory(username)
		table = ''

		if history != ['']:
			for row in history:
				row = row.split(' ')
				table += '{}{} {:<5.2f}  {}  {}\n' . format(SOLVED[int(row[0])], get_grow(float(row[3])), float(row[1]), row[2], sign(float(row[3])).ljust(5))

			count = database.getUserCount(username)
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
			bot.send_message(message.chat.id, table, reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам историю, так как вы ещё не играли', reply_markup=markup)


@bot.message_handler(commands=['my_score'])
def my_score(message):
	if validate(message):
		username = '@' + message.from_user.username

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		bot.send_message(message.chat.id, f'Ваш текущий счёт = {format(database.getUserScore(username))}', reply_markup=markup)


@bot.message_handler(commands=['my_level'])
def my_level(message):
	if validate(message):
		username = '@' + message.from_user.username

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, 'Ваш текущий уровень = ' + str('{:.2f}' . format(database.getUserLevel(username))), reply_markup=markup)


@bot.message_handler(commands=['my_rank'])
def my_rank(message):
	if validate(message):
		username = '@' + message.from_user.username

		count = database.getUserCount(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='❌ Скрыть', callback_data='back'))
		bot.send_message(message.chat.id, 'Ваш текущий ранг = ' + str(sudoku.getRank(round(database.getUserLevel(username)))), reply_markup=markup)


@bot.message_handler(commands=['change_theme'])
def change_theme(message, back_menu=False):
	if validate(message):
		username = '@' + message.from_user.username

		if database.isUserPlay(username):
			bot.send_message(message.chat.id, 'Пока вы не закончите решение судоку, тему нельзя будет изменить.')
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			for theme in field.THEMES.keys():
				if database.getTheme(username) != theme:
					markup.add(telebot.types.InlineKeyboardButton(text=field.THEMES[theme]['title'], callback_data='change_theme' + '_' + theme))
			if back_menu:
				markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_to_menu'))
			else:
				markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='back'))
			bot.send_message(message.chat.id, 'Выберите любую интересующую вас тему из списка ниже:', reply_markup=markup)


@bot.message_handler(commands=['change_mode'])
def change_mode(message):
	if validate(message):
		username = '@' + message.from_user.username

		if database.isUserPlay(username):
			bot.send_message(message.chat.id, 'Пока вы не закончите решение судоку, режим нельзя будет изменить.')
		else:
			if database.getGamemode(username) == 'challenge':
				freeplay_mode(message)
			else:
				challenge_mode(message)


@bot.message_handler(commands=['challenge_mode'])
def challenge_mode(message):
	if validate(message):
		username = '@' + message.from_user.username

		if database.getGamemode(username) == 'challenge':
			bot.send_message(message.chat.id, 'Вы уже играете в режиме challenge')
		elif database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Продолжить', callback_data='current_photo'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip'))
			markup.add(telebot.types.InlineKeyboardButton(text='🏳️ Сдаться', callback_data='give_up'))
			bot.send_message(message.chat.id, 'Пока вы не закончите решение текущего судоку, режим игры не выйдет', reply_markup=markup)
		else:
			database.setGamemode('challenge', username)
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Теперь вы играете в режиме challenge, это подразумевает, что после того, как вы начнёте игру, пойдёт отсчет времени и в зависимости от того, как быстро вы решите судоку, ваш уровень будет расти или понижаться', reply_markup=markup)


@bot.message_handler(commands=['freeplay_mode'])
def freeplay_mode(message):
	if validate(message):
		username = '@' + message.from_user.username

		if database.getGamemode(username) == 'freeplay':
			bot.send_message(message.chat.id, 'Вы уже играете в режиме freeplay')
		elif database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Продолжить', callback_data='current_photo'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip'))
			markup.add(telebot.types.InlineKeyboardButton(text='🏳️ Сдаться', callback_data='give_up'))
			bot.send_message(message.chat.id, 'Пока вы не закончите решение текущего судоку, режим игры не выйдет', reply_markup=markup)
		else:
			database.setGamemode('freeplay', username)
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Теперь вы играете в режиме freeplay, это подразумевает, что после того, как вы начнёте игру, отсчёта времени не последует, а ваш уровень не будет расти или понижаться', reply_markup=markup)


@bot.message_handler(commands=['open_cell'])
def open_cell(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		markup = telebot.types.InlineKeyboardMarkup()
		empty_rows = []
		for i, row in enumerate(database.getUserPuzzle(username)):
			if row.count(0) != 0:
				empty_rows.append(telebot.types.InlineKeyboardButton(text=f'{i + 1}-й ряд', callback_data='open_cell_row_' + str(i)))
		markup.add(*empty_rows)
		markup.add(telebot.types.InlineKeyboardButton(text='Отмена', callback_data='back'))

		field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserCurrent(username), solution=None, theme=database.getTheme(username))
		bot.send_photo(message.chat.id, open(database.others + 'sudoku.jpg', 'rb'), 'Для того, чтобы открыть любую пустую клетку в изначальном судоку вам необходимо сперва выбрать одну из неполностью заполненных строк:', reply_markup=markup)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['check_correctness'])
def check_correctness(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserCurrent(username), solution=database.getUserSolution(username), correct=True, theme=database.getTheme(username))
		AI.check_penalty(username)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='▶️Продолжить', callback_data='current_sudoku_not_delete'))
		bot.send_photo(message.chat.id, open(database.others + 'sudoku.jpg', 'rb'), reply_markup=markup)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['get_tip'])
def get_tip(message):
	if validate(message):
		username = '@' + message.from_user.username

		if database.isUserPlay(username):
			penalty_cell = AI.avg_time(database.getUserLevel(username)) * AI.cell_penalty_koef * 60
			penalty_check = AI.avg_time(database.getUserLevel(username)) * AI.check_penalty_koef * 60

			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text=f'Открыть незаполненную клетку (+{penalty_cell:.0f})', callback_data='open_cell'))
			markup.add(telebot.types.InlineKeyboardButton(text=f'Проверить заполненные клетки (+{penalty_check:.0f})', callback_data='check_correctness'))
			markup.add(telebot.types.InlineKeyboardButton(text='Подсветить цифру (+0)', callback_data='highlight_num'))
			markup.add(telebot.types.InlineKeyboardButton(text='Показать стеки (+0)', callback_data='possible'))
			markup.add(telebot.types.InlineKeyboardButton(text='Отмена', callback_data='back'))
			
			bot.send_message(message.chat.id, f'💡Выберите интересующую вас подсказку из доступных ниже. Обратите внимание на то, что за разные подсказки могут накладываться различные штрафы ко времени решения в виде некотрого количества секунд.', reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['possible'])
def possible(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserCurrent(username), possible=True, theme=database.getTheme(username))
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='▶️Продолжить', callback_data='current_photo_not_delete'))
		bot.send_photo(message.chat.id, open(database.others + 'sudoku.jpg', 'rb'), reply_markup=markup)
	else:
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
		bot.send_message(message.chat.id, 'Я не могу показать вам стеки (возможные числа) так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['current_text'])
def current_text(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text=f'{NUM[3]}✖️{NUM[6]}', callback_data='current_emoji'), telebot.types.InlineKeyboardButton(text='🌇', callback_data='current_photo'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip_not_delete'))
			bot.send_message(message.chat.id, sudoku.getStrPuzzle(database.getUserCurrent(username)), reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам текущее судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['current_emoji'])
def current_emoji(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='[9, 0, 5]', callback_data='current_text'), telebot.types.InlineKeyboardButton(text='🌇', callback_data='current_photo'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip_not_delete'))
			bot.send_message(message.chat.id, convert_to_emoji(database.getUserCurrent(username)), reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам текущее судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['current_photo'])
def current_photo(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='[9, 0, 5]', callback_data='current_text'), telebot.types.InlineKeyboardButton(text=f'{NUM[3]}✖️{NUM[6]}', callback_data='current_emoji'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip_not_delete'))
			field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserCurrent(username), theme=database.getTheme(username))
			photo = open(database.others + 'sudoku.jpg', 'rb')
			bot.send_photo(message.chat.id, photo, reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам текущее судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['current_sudoku'])
def current_sudoku(message):
	if validate(message):
		username = '@' + message.from_user.username

		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='[9, 0, 5]', callback_data='current_text'), telebot.types.InlineKeyboardButton(text=f'{NUM[3]}✖️{NUM[6]}', callback_data='current_emoji'), telebot.types.InlineKeyboardButton(text='🌇', callback_data='current_photo'))
			bot.send_message(message.chat.id, 'Выберите подходящий вам формат из списка ниже:', reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам текущее судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['initial_text'])
def initial_text(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text=f'{NUM[3]}✖️{NUM[6]}', callback_data='initial_emoji'), telebot.types.InlineKeyboardButton(text='🌇', callback_data='initial_photo'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip_not_delete'))
			bot.send_message(message.chat.id, sudoku.getStrPuzzle(database.getUserPuzzle(username)), reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам начальное судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['initial_emoji'])
def initial_emoji(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='[9, 0, 5]', callback_data='initial_text'), telebot.types.InlineKeyboardButton(text='🌇', callback_data='initial_photo'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip_not_delete'))
			bot.send_message(message.chat.id, convert_to_emoji(database.getUserPuzzle(username)), reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам начальное судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['initial_photo'])
def initial_photo(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='[9, 0, 5]', callback_data='initial_text'), telebot.types.InlineKeyboardButton(text=f'{NUM[3]}✖️{NUM[6]}', callback_data='initial_emoji'))
			markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip_not_delete'))
			field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserPuzzle(username), theme=database.getTheme(username))
			photo = open(database.others + 'sudoku.jpg', 'rb')
			bot.send_photo(message.chat.id, photo, reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам начальное судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['initial_sudoku'])
def initial_sudoku(message):
	if validate(message):
		username = '@' + message.from_user.username
		
		if database.isUserPlay(username):
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='[9, 0, 5]', callback_data='initial_text'), telebot.types.InlineKeyboardButton(text=f'{NUM[3]}✖️{NUM[6]}', callback_data='initial_emoji'), telebot.types.InlineKeyboardButton(text='🌇', callback_data='initial_photo'))
			bot.send_message(message.chat.id, 'Выберите подходящий вам формат из списка ниже', reply_markup=markup)
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игру', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Я не могу показать вам начальное судоку, так как вы ещё не начали игру', reply_markup=markup)


@bot.message_handler(commands=['give_up'])
def give_up(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username

	if database.isUserPlay(username):
		AI.recount_level(username, True)
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Новое судоку', callback_data='next_sudoku'))
		bot.send_message(message.chat.id, 'Вы сдались. Если хотите, то можете начать новую игру', reply_markup=markup)
		database.resetUserTime(username)
	else:
		bot.send_message(message.chat.id, 'Вы ещё не начали игру')


@bot.message_handler(commands=['next_sudoku'])
def next_sudoku(message):
	if not validate(message):
		return
	username = '@' + message.from_user.username
	
	if database.isUserPlay(username):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='▶️ Продолжить', callback_data='current_photo'), telebot.types.InlineKeyboardButton(text='🏳️ Сдаться', callback_data='give_up'))
		markup.add(telebot.types.InlineKeyboardButton(text='💡 Подсказки', callback_data='get_tip'))
		bot.send_message(message.chat.id, 'Вы ещё не закончили сборку прошлой головоломки, если у вас возникли проблемы или с решением текущего судоку, то вы можете воспользоваться подсказками или сдаться.', reply_markup=markup)
	else:
		database.nextPuzzle(username)
		database.setUserTime(datetime.datetime.today(), username)
		initial_photo(message)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
	message = call.message
	message.from_user = call.from_user

	#bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за честный ответ!')
	if call.data == 'possible':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		possible(message)
	if call.data == 'possible_not_delete':
		possible(message)
	if call.data == 'change_mode':
		change_mode(message)
	if call.data == 'another_format':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		current_sudoku(message)
	if call.data in ['menu', 'back_to_menu']:
		bot.delete_message(call.message.chat.id, call.message.message_id)
		menu(message)
	if call.data == 'back_to_menu_clean':
		menu(message)
	if call.data == 'raitings':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		raitings(message, True)
	if call.data == 'level_raiting':
		level_raiting(message)
	if call.data == 'score_raiting':
		score_raiting(message)
	if call.data == 'success_raiting':
		success_raiting(message)
	if call.data == 'count_raiting':
		count_raiting(message)
	if call.data == 'stats':
		stats(message)
	if call.data == 'history':
		history(message)
	if call.data == 'level_graphics':
		level_graphics(message)
	if call.data == 'my_level':
		my_level(message)
	if call.data == 'my_score':
		my_score(message)
	if call.data == 'my_rank':
		my_rank(message)
	if call.data == 'methods':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		methods(message, True)
	if call.data == 'authors':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		authors(message)
	if call.data == 'system':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		system(message)
	if call.data == 'rules':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		rules(message)
	if call.data == 'manual':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		manual(message)
	if call.data == 'help':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		help(message, True)
	if call.data == 'back_to_help':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		help(message)
	if call.data == 'next_sudoku_from_manual':
		for i in range(0, 8):
			bot.delete_message(call.message.chat.id, call.message.message_id - i)
		next_sudoku(message)
	if call.data == 'back_to_help_from_manual':
		for i in range(0, 8):
			bot.delete_message(call.message.chat.id, call.message.message_id - i)
		help(message)
	if call.data == 'next_sudoku_not_delete':
		if database.isUserPlay('@' + call.from_user.username):
			next_sudoku(message)
		else:
			next_sudoku(message)
			bot.answer_callback_query(callback_query_id=call.id, text='Время пошло!')	
	if call.data == 'next_sudoku':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		if database.isUserPlay('@' + call.from_user.username):
			next_sudoku(message)
		else:
			next_sudoku(message)
			bot.answer_callback_query(callback_query_id=call.id, text='Время пошло!')		
	if call.data == 'password':
		password(message)		
	if call.data == 'give_up':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		give_up(message)
	if call.data == 'reg':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		start(message)
	if call.data == 'records':
		records(message)
	if call.data == 'back':
		bot.delete_message(call.message.chat.id, call.message.message_id)
	if call.data == 'get_tip_not_delete':
		get_tip(message)
	if call.data == 'get_tip':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		get_tip(message)
	if call.data == 'current_sudoku':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		current_sudoku(message)
	if call.data == 'current_sudoku_not_delete':
		current_sudoku(message)
	if call.data == 'initial_sudoku':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		initial_sudoku(message)
	if call.data == 'current_text':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		current_text(message)
	elif call.data == 'current_emoji':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		current_emoji(message)
	elif call.data == 'current_photo':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		current_photo(message)
	elif call.data == 'current_photo_not_delete':
		current_photo(message)
	elif call.data == 'initial_text':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		initial_text(message)
	elif call.data == 'initial_emoji':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		initial_emoji(message)
	elif call.data == 'initial_photo':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		initial_photo(message)
	elif call.data == 'initial_photo_not_delete':
		initial_photo(message)
	elif call.data == 'check_correctness':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		check_correctness(message)
		bot.answer_callback_query(callback_query_id=call.id, text='Правильно заполненные клетки подсвечены зелёным цветом, неправильно заполненные - красным, изначально заполненные и совсем не заполненные клетки не подсвечены.', show_alert=True)
	elif call.data == 'open_cell':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		open_cell(message)
	elif call.data == 'change_theme':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		change_theme(message, True)
	elif call.data[:12] == 'change_theme':
		database.setTheme(call.data[13:], '@' + call.message.from_user.username)
		bot.answer_callback_query(callback_query_id=call.id, text='Тема успешно изменена, наслаждайтесь!')
	elif call.data[:-2] == 'open_cell_row':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		row = int(call.data[-1])
		username = '@' + call.message.from_user.username

		if database.getUserPuzzle(username)[row].count(0) == 0:
			return
		markup = telebot.types.InlineKeyboardMarkup()
		empty_cols = []
		for j, num in enumerate(database.getUserPuzzle(username)[row]):
			if num == 0:
				empty_cols.append(telebot.types.InlineKeyboardButton(text=f'{j + 1}-й столбец', callback_data='open_cell_col_' + str(row) + '_'+ str(j)))
		markup.add(*empty_cols)
		markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='open_cell'))

		field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserCurrent(username), solution=None, theme=database.getTheme(username))
		bot.send_photo(message.chat.id, open(database.others + 'sudoku.jpg', 'rb'), f'Вы выбрали {row + 1}-й ряд, теперь выберите один из столбцов в этом ряду:', reply_markup=markup)
	elif call.data[:-4] == 'open_cell_col':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		row = int(call.data[-3])
		col = int(call.data[-1])
		username = '@' + call.message.from_user.username
		if database.getUserPuzzle(username)[row][col] != 0:
			return
		database.updateUserPuzzle(row, col, username)
		field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=database.getUserCurrent(username), opened=(row, col), theme=database.getTheme(username))
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='▶️Продолжить', callback_data='current_photo_not_delete'))
		bot.send_photo(message.chat.id, open(database.others + 'sudoku.jpg', 'rb'), reply_markup=markup)
		bot.answer_callback_query(callback_query_id=call.id, text=f'Клетка в {row + 1}-ом ряду, {col + 1}-ом столбце открыта')
	elif call.data == 'delete_me':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		unreg(message)


@bot.edited_message_handler(func=lambda message: True)
@bot.message_handler(content_types=['text'])
def text_message(message):
	if validate(message):
		username = '@' + message.from_user.username

		if message.text[0] == '/':
			bot.send_message(message.chat.id, 'Такой команды я не знаю, попобуйте воспользоваться списком комманд или меню')
		elif message.text[0] == '@':
			data = message.text.split(' ')
			if username == data[0]:
				bot.send_message(message.chat.id, 'Не ну не свой же ник вводить для восстановления нужно')
			elif database.isUserPlay(username):
				markup = telebot.types.InlineKeyboardMarkup()
				markup.add(telebot.types.InlineKeyboardButton(text='▶️ Продолжить', callback_data='current_photo'), telebot.types.InlineKeyboardButton(text='🏳️ Сдаться', callback_data='give_up'))
				bot.send_message(message.chat.id, 'Вы еще не закончили сборку судоку, пока не закончите, восстановление будет недоступно', reply_markup=markup)
			elif len(data) != 2:
				bot.send_message(message.chat.id, 'Неверный формат ввода (см. примечания к восстановленю данных)')
			elif not database.isUserExist(data[0]):
				bot.send_message(message.chat.id, 'Такого пользователя нет в моей базе данных')
			elif data[1] != database.getPassword(data[0]):
				database.updatePassword(data[0])
				bot.send_message(message.chat.id, 'Неверный пароль, пароль был обновлён')
			else:
				database.recovery(username, data[0], data[1])
				bot.send_message(message.chat.id, 'Данные были успешно восстановлены')
		elif database.isUserPlay(username):
			puzzle_1 = checkTextMessage(message)
			puzzle_2 = checkEmojiMessage(message)
			puzzle = None

			if type(puzzle_1) is str and type(puzzle_2) is str:
				bot.send_message(message.chat.id, puzzle_1)
				return
			elif type(puzzle_1) is not str:
				puzzle = puzzle_1
			else:
				puzzle = puzzle_2

			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='▶️ Продолжить', callback_data='current_photo'), telebot.types.InlineKeyboardButton(text='🏳️ Сдаться', callback_data='give_up'))

			if not sudoku.are_equal(puzzle, database.getUserPuzzle(username)):
				bot.send_message(message.chat.id, 'Вы прислали не то судоку', reply_markup=markup)
			elif not sudoku.isCorrect(puzzle):
				field.draw_sudoku(puzzle=database.getUserPuzzle(username), current=puzzle, invalid=True, theme=database.getTheme(username))
				photo = open(database.others + 'sudoku.jpg', 'rb')
				bot.send_photo(message.chat.id, photo)
				bot.send_message(message.chat.id, 'Судоку заполнено с ошибками (повтор с блоке/строке/столбце)', reply_markup=markup)	
			elif not sudoku.isSolved(puzzle):
				database.setUserCurrent(puzzle, username)
				current_photo(message)
			elif database.isCorrectSolution(puzzle, username):
				database.setUserCurrent(puzzle, username)
				field.draw_sudoku(puzzle=database.getUserPuzzle(username), solution=database.getUserCurrent(username), solved=True, theme=database.getTheme(username))

				time = database.convert(database.solvingTime(username))
				markup = telebot.types.InlineKeyboardMarkup()
				markup.add(telebot.types.InlineKeyboardButton(text='Новое судоку', callback_data='next_sudoku_not_delete'))
				bot.send_photo(message.chat.id, open(database.others + 'sudoku.jpg', 'rb'), 'Поздравляю, вы правильно решили судоку!\nВремя решения: {}' . format(time), reply_markup=markup)

				diff = database.getUserLevel(username)
				time = database.solvingTime(username)

				if database.is_new_record(time, diff):
					prev = database.get_record(diff)
					bot.send_message(message.chat.id, f'🏆Вы установили новый рекорд!\nПредыдущий рекорд:\n{database.getUserLevel(username):.0f}:  {prev[0]} - {prev[1]}')
					database.update_record(time, diff, username)

				AI.recount_level(username)
				database.resetUserTime(username)
			else:
				bot.send_message(message.chat.id, 'Увы, но решение неправильное')
		else:
			markup = telebot.types.InlineKeyboardMarkup()
			markup.add(telebot.types.InlineKeyboardButton(text='Начать игры', callback_data='next_sudoku'))
			bot.send_message(message.chat.id, 'Вы пока не начали игру', reply_markup=markup)


def validate(message) -> bool:
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Похоже, что у вас не задан username (имя пользователя вида @User). Пока username не задан, я не могу зарегестрировать вас в базе данных.')
		return False
	elif not database.isUserExist('@' + message.from_user.username):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(telebot.types.InlineKeyboardButton(text='Зарегестрироваться', callback_data='reg'))
		bot.send_message(message.chat.id, 'Вы пока не зарегестрированы, возможно произошёл сбой.', reply_markup=markup)
		return False
	else:
		database.udateLastUserActivity('@' + message.from_user.username)
		return True


def alert():
	while True:
		for user in database.unactive_users(14):
			try:
				bot.send_message(database.getID(user), 'От вас за последние 14 дней не было никакой активности, мне пришлось удалить вас из базы дынных')
			except telebot.apihelper.ApiException:
				pass
			database.deleteUser(user)
			print(f'DELETED: {user}')
		for user in database.unactive_users(2):
			if database.isUserPlay(user):
				AI.recount_level(user, True)
			database.resetUserTime(user)
			if (datetime.datetime.today() - database.getLastUserAlert(user)).days >= 1:
				delta = datetime.datetime.today() - database.getLastUserActivity(user)
				print(f'ALERTED: {user} {delta}')
				try:
					bot.send_message(database.getID(user), f'От вас за последние {delta.days} дней и {delta.seconds // 3600} часа(ов) не было никакой активности.')
					markup = telebot.types.InlineKeyboardMarkup()
					markup.add(telebot.types.InlineKeyboardButton(text='Удалить профиль', callback_data='delete_me'))
					bot.send_message(database.getID(user), 'По истечению 14 суток мне прийдется удалить вас и все ваши игровые достижения из базы данных. Если вы хотите отключить напоминания, вы можете самостоятельно выйти из игры с потерей всех данных, удалив свой профиль', reply_markup=markup)
				except telebot.apihelper.ApiException:
					database.deleteUser(user)
				else:
					database.udateLastUserAlert(user)
		sleep(60)

#start_new_thread(alert, ())
start_new_thread(backup.run, ())

bot.polling(none_stop = True, interval = 0)
# python C:\Users\HP_650\Desktop\Python_BOT\bot.py
