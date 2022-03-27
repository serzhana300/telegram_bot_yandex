import config
import sqlite3
import telebot
import re
from telebot import types


def check_num(string):
    phone = re.sub(r'\b\D', '', string)
    clear_phone = re.sub(r'[\ \(]?', '', phone)
    if re.findall(r'^[\+7|8]*?\d{10}$', clear_phone) or re.match(r'^\w+[\.]?(\w+)*\@(\w+\.)*\w{2,}$',string):
        return True
    else: return False


bot = telebot.TeleBot(config.TOKEN)
user_name, number_phone, order = '', '', ''


@bot.message_handler(commands=["add"])
def cmd_add(message):
    u_id = message.chat.id

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f"""SELECT user_id FROM users WHERE user_id = {message.chat.id}""")
    data = cursor.fetchall()
    if not data:
        cursor.execute(f"""INSERT INTO users VALUES({u_id});""")
        bot.send_message(message.chat.id, 'Спасибо за участие в системе!')
        connect.commit()
    else:
        bot.send_message(message.chat.id, 'Вы уже учавствуете в системе бонусов.')


@bot.message_handler(commands=['delete'])
def delete(msg):

    u_id = msg.chat.id

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute(f"""DELETE FROM users WHERE user_id = {u_id}""")
    connect.commit()
    bot.send_message(u_id, 'Вы вышли из системы бонусов.')


@bot.message_handler(commands=['start'])
def hello(msg):
    id = msg.chat.id

    markup_inline = types.InlineKeyboardMarkup()
    item_rolls = types.InlineKeyboardButton(text='Хочу роллы', callback_data='Хочу роллы')
    item_woks = types.InlineKeyboardButton(text='Хочу вок', callback_data='Хочу вок')
    item_set = types.InlineKeyboardButton(text='Хочу Сет', callback_data='Хочу сет')

    markup_inline.add(item_rolls, item_woks, item_set)

    bot.send_message(id, '''Приветсвую вас! Я бот-помощник компании Yandex Sushi
                         Мы рады приветсвовать вас!
                         Для заказа роллов напишите: "Хочу роллы"
                         Для заказа вока напишите: "Хочу вок"
                         Для заказа наборов суши напишите: "Хочу сет"
                         ''', reply_markup=markup_inline)


@bot.callback_query_handlers(func=lambda call: True)
def answer(call):
    id = call.mesage.chat.id
    if call.data == 'Хочу роллы':
        bot.send_message(id, 'Хочу роллы')
    if call.data == 'Хочу вок':
        bot.send_message(id, 'Хочу вок')
    if call.data == 'Хочу сет':
        bot.send_message(id, 'Хочу сет')


@bot.message_handler(content_types=['text'])
def get_text(message):
    global user_name, number_phone, order
    id = message.chat.id
    if message.text.lower() == 'хочу роллы':
        bot.send_message(id, 'Прекрасный выбор!')
        bot.send_message(id, 'Как я могу к вам обращаться?')
    if message.text.lower() == 'хочу вок':
        bot.send_message(id, 'Прекрасный выбор!')
        bot.send_message(id, 'Как я могу к вам обращаться?')
    if message.text.lower() == 'хочу сет':
        bot.send_message(id, 'Прекрасный выбор!')
        bot.send_message(id, 'Как я могу к вам обращаться?')
    if check_num(message.text):
        bot.send_message(id, 'Спасибо за внимание')
    else:
        bot.send_message(id, f'{message.text}, Приятно познакомитсья! Укажите ваш номер телефона, пожалуйста.')
        user_name = message.text


if __name__ == '__main__':
    bot.polling(none_stop=True)