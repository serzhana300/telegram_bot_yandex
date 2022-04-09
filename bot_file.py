import config
import sqlite3
import telebot
import re
from telebot import types


FLAG = ''
cont_order = True


def check_num(string):
    phone = re.sub(r'\b\D', '', string)
    clear_phone = re.sub(r'[\ \(]?', '', phone)
    if re.findall(r'^[\+7|8]*?\d{10}$', clear_phone) or re.match(r'^\w+[\.]?(\w+)*\@(\w+\.)*\w{2,}$',string):
        return True
    else: return False


bot = telebot.TeleBot(config.TOKEN)
user_name, number_phone, order = '', '', []


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
    global FLAG
    id = msg.chat.id

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    bt_rolls = types.KeyboardButton(text='Хочу роллы')
    bt_wok = types.KeyboardButton(text='Хочу вок')
    bt_set = types.KeyboardButton(text='Хочу сет')
    kb.add(bt_set, bt_rolls, bt_wok)

    bot.send_message(id, '''Приветсвую вас! Я бот-помощник компании Yandex Sushi
                         Мы рады приветсвовать вас!
                         Для заказа роллов напишите: "Хочу роллы"
                         Для заказа вока напишите: "Хочу вок"
                         Для заказа наборов суши напишите: "Хочу сет"
                         ''', reply_markup=kb)
    FLAG = 'continue_start'


@bot.message_handler(content_types=['text'])
def get_text(message):
    global user_name, number_phone, order, FLAG
    id = message.chat.id
    if FLAG == 'continue_oform':
        n = ''
        for i in order:
            n += f'{i[0]} - {i[1]}x\n'
        if message.text == 'Да':
            strin = f"""!СПАСИБО ЗА ЗАКАЗ!
Ваш заказ:
{n} Заказ находится в обработке, ожидайте связи с оператором по вышеуказанному номеру!"""
            bot.send_message(id, strin)
        elif message.text == 'Нет':
            bot.send_message(id, 'Хорошо, мы отменили вашу заявку, спасибо за выбор нашего сервиса!')

    if FLAG == 'continue_start':
        if message.text.lower() == 'хочу роллы':
            if user_name:
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name FROM rolls""")
                data = cursor.fetchall()
                n = ''
                for i in data:
                    if i:
                        n += f'{i}\n'
                bot.send_message(id, 'Прекрасный выбор!')
                pic = open('brosh_pic/rolls_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                bot.send_message(id, f"""Вот что мы можем вам предложить:{n}""")
                FLAG = 'continue_roll'
            else:
                bot.send_message(id, 'Прекрасный выбор!')
                bot.send_message(id, 'Как я могу к вам обращаться?')
                FLAG = 'continue_roll'
            print('aaaa')
        if message.text.lower() == 'хочу вок':
            bot.send_message(id, 'Прекрасный выбор!')
            bot.send_message(id, 'Как я могу к вам обращаться?')
            FLAG = 'continue_wok'
        if message.text.lower() == 'хочу сет':
            bot.send_message(id, 'Прекрасный выбор!')
            bot.send_message(id, 'Как я могу к вам обращаться?')
            FLAG = 'continue_set'
    elif FLAG == 'continue_roll':
        if message.text == 'Да':
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_rolls = types.KeyboardButton(text='Хочу роллы')
            bt_wok = types.KeyboardButton(text='Хочу вок')
            bt_set = types.KeyboardButton(text='Хочу сет')
            kb.add(bt_set, bt_rolls, bt_wok)

            bot.send_message(id, '''Приветсвую вас! Я бот-помощник компании Yandex Sushi
                                     Мы рады приветсвовать вас!
                                     Для заказа роллов напишите: "Хочу роллы"
                                     Для заказа вока напишите: "Хочу вок"
                                     Для заказа наборов суши напишите: "Хочу сет"
                                     ''', reply_markup=kb)
            FLAG = 'continue_start'
        elif message.text == 'Нет':
            n = ''
            for i in order:
                n += f'{i[0]} - {i[1]}x\n'
            stri = f"""Прекрасно! Что же у нас в корзине?
_________________

{n}
_________________

Передать заказ администратору?"""
            bot.send_message(id, stri)
            FLAG = 'continue_oform'
        elif not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.upper()}, введите ваш номер телефона')
        elif user_name and not number_phone:
            if check_num(message.text):
                connect = sqlite3.connect('eat.db')

                cursor = connect.cursor()
                cursor.execute(f"""SELECT name FROM rolls""")
                data = cursor.fetchall()
                n = ''
                for i in data:
                    if i:
                        n += f'{i[0]}\n'
                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                pic = open('brosh_pic/rolls_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                bot.send_message(id, f"""Вот что мы можем вам предложить:
{n}""")
                number_phone = message.text
            else:
                bot.send_message(id, 'Номер некорректен...')
        elif user_name and number_phone and cont_order:
            f = False
            for i in order:
                if i[0] == message.text:
                    order[order.index(i)][1] += 1
                    print(i)
                    f = True
            if not f:
                order.append([message.text, 1])
            bot.send_message(id, 'Мы записали, что-то еще?')

    elif FLAG == 'continue_wok':
        if not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.upper()}, введите ваш номер телефона')
        elif user_name and not number_phone:
            if check_num(message.text):
                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                # pic = open('---', 'rb')
                # bot.send_photo(id, pic, caption='Вот что мы можем предложить:')
            else:
                bot.send_message(id, 'Номер некорректен...')
        elif user_name and number_phone:
            order.append(message.text)
            bot.send_message(id, 'Мы записали, что-то еще?')
    elif FLAG == 'continue_set':
        if not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.upper()}, введите ваш номер телефона')
        elif user_name and not number_phone:
            if check_num(message.text):
                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                # pic = open('---', 'rb')
                # bot.send_photo(id, pic, caption='Вот что мы можем предложить:')
            else:
                bot.send_message(id, 'Номер некорректен...')
        elif user_name and number_phone:
            order.append(message.text)
            bot.send_message(id, 'Мы записали, что-то еще?')
    elif FLAG == '':
        pass
    elif FLAG == '':
        pass
    else:
        bot.send_message(id, 'Я не понял вашу команду...')
        user_name = message.text


if __name__ == '__main__':
    bot.polling(none_stop=True)