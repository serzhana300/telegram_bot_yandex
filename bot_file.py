# используемые библиотеки
import json
import pprint
import random

import config
import sqlite3
import telebot
import re
import requests

from telebot import types

FLAG = ''
status_bar = ''
cont_order = True
values = []


# проверка номера телефона
def check_num(string):
    phone = re.sub(r'\b\D', '', string)
    clear_phone = re.sub(r'[\ \(]?', '', phone)
    if re.findall(r'^[\+7|8]*?\d{10}$', clear_phone) or re.match(r'^\w+[\.]?(\w+)*\@(\w+\.)*\w{2,}$', string):
        return True
    else:
        return False


bot = telebot.TeleBot(config.TOKEN)
user_name, number_phone, order = '', '', []


@bot.message_handler(commands=['admin_console'])
# настройка администратора
def admin_console(message):
    global FLAG
    id = message.chat.id

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    bt_rolls = types.KeyboardButton(text='***')
    kb.add(bt_rolls)

    bot.send_message(id, '''
This console was created to assign an account to accept orders.
Please enter the password key to assign this account to the administrative.
''', reply_markup=kb)

    FLAG = 'ADMIN'

@bot.message_handler(commands=['start'])
# начало общения с пользователем

def start(message):
    global FLAG
    id = message.chat.id

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    bt_rolls = types.KeyboardButton(text='Хочу роллы')
    bt_wok = types.KeyboardButton(text='Хочу вок')
    bt_set = types.KeyboardButton(text='Хочу сет')
    bt_ju = types.KeyboardButton(text='Хочу морс')
    kb.add(bt_set, bt_rolls, bt_wok, bt_ju)

    bot.send_message(id, '''Добрый день ! 😃 
Я - бот-помощник(Yandex Sushi)
Я могу вас предоставить:
•роллы
•вок
•сет
•морс
Для заказа напишите ,,Хочу …(выбранное вами блюдо)’’
''', reply_markup=kb)
    FLAG = 'continue_start'


@bot.message_handler(commands=["check_bonus"])
# проверка на участие в бонусной программе

def cmd_add(message):
    u_id = message.chat.id

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f"""SELECT user_id,
       phone_number,
       name_pers,
       balance
  FROM users WHERE user_id == '{message.chat.id}';""")
    data = cursor.fetchall()

    if not data:
        bot.send_message(message.chat.id, 'Вы не учавствуете в системе.\n'
                                          'Сделайте 1 заказ, чтобы стать участником системы')
    else:
        bot.send_message(message.chat.id, f'Вы уже учавствуете в системе бонусов.\nВаше имя: {data[0][2]}\n'
                                          f'Ваш номер телефона: {data[0][1]}\n'
                                          f'Ваш баланс: {data[0][3]}')


@bot.message_handler(commands=['delete'])
# возможность удаления из бонусной программы
def delete(msg):
    u_id = msg.chat.id

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute(f"""DELETE FROM users WHERE user_id = {u_id}""")
    connect.commit()
    bot.send_message(u_id,
                     'Вы вышли из системы бонусов.')


@bot.message_handler(content_types=['text'])
def get_text(message):
    global user_name, number_phone, order, FLAG, values
    id = message.chat.id
    if message.text == '/start':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

        bt_rolls = types.KeyboardButton(text='Хочу роллы')
        bt_wok = types.KeyboardButton(text='Хочу вок')
        bt_set = types.KeyboardButton(text='Хочу сет')
        bt_ju = types.KeyboardButton(text='Хочу морс')

        kb.add(bt_set, bt_rolls, bt_wok, bt_ju)

        bot.send_message(id, '''Добрый день ! 😃 
Я - бот-помощник(Yandex Sushi)
Я могу вас предоставить:
•роллы
•вок
•сет
•морс
Для заказа напишите ,,Хочу …(выбранное вами блюдо)’’
                                     ''', reply_markup=kb)
        FLAG = 'continue_start'

    if FLAG == '':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        bt_rolls = types.KeyboardButton(text='Хочу роллы')
        bt_wok = types.KeyboardButton(text='Хочу вок')
        bt_set = types.KeyboardButton(text='Хочу сет')
        bt_ju = types.KeyboardButton(text='Хочу морс')
        kb.add(bt_set, bt_rolls, bt_wok, bt_ju)

        bot.send_message(id, '''Добрый день ! 😃 
Я - бот-помощник(Yandex Sushi)
Я могу вас предоставить:
•роллы
•вок
•сет
•морс
Для заказа напишите ,,Хочу …(выбранное вами блюдо)’’
                             ''', reply_markup=kb)
        FLAG = 'continue_start'

    elif FLAG == 'ADMIN':
        if message.text == '***':
            pass
        elif message.text == 'n-X5-G-rwl-C':

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT ID_ADMIN FROM ADMIN""")
            data = cursor.fetchall()
            f = data[0][0]
            cursor.execute(f"""DELETE FROM ADMIN
      WHERE ID_ADMIN = {f};""")
            cursor.execute(f"""INSERT INTO ADMIN (
                      ID_ADMIN
                  )
                  VALUES (
                      {id}
                  );""")
            connect.commit()
            print(id)
            bot.send_message(id, 'This account is assigned by the bot administrator.')
    elif FLAG == 'continue_oform':
        def verif_order():
            u_id = message.chat.id

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT user_id,
                   phone_number,
                   name_pers,
                   balance
              FROM users WHERE user_id == {u_id};""")
            data = cursor.fetchall()
            if not data:
                return False
            else:
                return True

        kb_start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        bt_start = types.KeyboardButton(text='/start')
        film_kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        yes_bt = types.KeyboardButton(text='Посмотреть фильм🎥')
        no_bt = types.KeyboardButton(text='Нет, спасибо')
        film_kb.add(yes_bt, no_bt)
        kb_start.add(bt_start)

        kbb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        bt_yes = types.KeyboardButton(text='Хочу!')
        bt_not = types.KeyboardButton(text='Нет, спасибо')
        kbb.add(bt_yes, bt_not)
        kb_smile = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btfl = types.KeyboardButton(text='😍')
        kb_smile.add(btfl)
        n = ''

        for i in order:
            n += f'{i[0]} - {i[1]}x\n'

        if message.text == '😍':
            bot.send_message(id, 'Мы знали что вам понравится! <3', reply_markup=kb_start)

        elif message.text.lower() == 'да, все верно':
            strin = f"""Благодарим за заказ !😉
В вашем заказе находится:\n
{n}
____________________
Заказ обрабатывается, ждите дальнейшего оповещения по номеру, который вы указали в заказе ! 😃"""
            bot.send_message(id, strin)
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT ID_ADMIN FROM ADMIN""")
            data = cursor.fetchall()
            val = data[0][0]
            bot.send_message(val, f"""Имя: {user_name},
Номер телефона: {number_phone},
Заказ: {n}""")
            f = True

            if not verif_order():
                bot.send_message(id, 'Вы совершили 1 заказ в нашем магазине! '
                                     'Вы хотите учавствовать в бонусной системе нашего ресторана?',
                                 reply_markup=kbb)
                f = False
            if f:
                bot.send_message(id, 'Мы можем посоветовать вам фильм🎥', reply_markup=film_kb)

        elif message.text.lower() == 'посмотреть фильм🎥':
            res_city = requests.get(
                f'https://imdb-api.com/ru/API/Top250Movies/k_z7ny8kho'
            )
            cash = json.loads(res_city.content)['items']
            strok = 'Под приятные роллы можно и приятный фильм посмотреть😜\n' \
                    'Вот что мы можем предложить😉\n'

            for i in range(3):
                create_strok = '\n🔥'
                val = random.choice(cash)
                create_strok += f"{val['fullTitle']}\n"
                create_strok += f"Рейтинг: {val['imDbRating']}\n"
                create_strok += f"Год выхода: {val['year']}\n"
                strok += create_strok

            photo = open('brosh_pic/film.jpg', 'rb')
            bot.send_photo(id, photo, caption=strok, reply_markup=kb_smile)

        elif message.text.lower() == 'хочу!':
            bot.send_message(id, 'Прекрасно! Сейчас мы вас зарегестрируем!')

            u_id = message.chat.id
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT user_id,
                   phone_number,
                   name_pers,
                   balance
              FROM users WHERE user_id == '{message.chat.id}';""")
            data = cursor.fetchall()

            if not data:
                cursor.execute(f"""INSERT INTO users (
                                  user_id,
                                  phone_number,
                                  name_pers,
                                  balance
                              )
                              VALUES (
                                  '{u_id}',
                                  '{number_phone}',
                                  '{user_name}',
                                  '{'0'}'
                              );""")
                bot.send_message(message.chat.id, 'Спасибо за участие в системе!')
                bot.send_message(message.chat.id, f'Вы учавствуете в системе бонусов.\nВаше имя: {user_name}\n'
                                                  f'Ваш номер телефона: {number_phone}\n'
                                                  f'Ваш баланс: 0 баллов')
                connect.commit()
            else:
                bot.send_message(message.chat.id, f'Вы уже учавствуете в системе бонусов.\nВаше имя: {data[0][2]}\n'
                                                  f'Ваш номер телефона: {data[0][1]}\n'
                                                  f'Ваш баланс: {data[0][3]} баллов')
        elif message.text.lower() == 'изменить':
            bot.send_message(id, 'Для изменения заказа, вам надо сделать повторный заказ.', reply_markup=kb_start)
            FLAG = ''
        elif message.text.lower() == 'нет, спасибо':
            bot.send_message(id, 'Хорошо, ожидайте звонка от оператора!\nСпасибо за заказ!', reply_markup=kb_start)
            FLAG = ''

    elif FLAG == 'continue_start':

        if message.text.lower() == 'хочу роллы':
            values = []
            kb_skip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_s = types.KeyboardButton(text='-поля для заполнения пользователем-')
            kb_skip.add(bt_s)

            if user_name:
                order.clear()
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM rolls""")
                data = cursor.fetchall()

                if message.text in values:
                    f = False
                    for i in order:
                        if i[0] == message.text:
                            cos = 0
                            for b in data:
                                if message.text == b[0]:
                                    cos = b[1]
                            order[order.index(i)][1] += 1
                            order[order.index(i)][2] = cos
                            print(i)
                            f = True

                    if not f:
                        cos = 0
                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order.append([message.text, 1, cos])
                    bot.send_message(id, 'Мы записали, что-то еще?')
                else:
                    if 'хочу' not in str(message.text.lower()).split():
                        bot.send_message(id, 'Такого блюда нет в наших списках.')
                n = ''
                for i in order:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'
                bot.send_message(id, 'Прекрасный выбор!')
                pic = open('brosh_pic/rolls_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                kb_rolls = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

                bt_yd = types.KeyboardButton(text='Ролл Фудзи')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_yd_2 = types.KeyboardButton(text='Калифорния сяке с икрой')
                bt_lapsh = types.KeyboardButton(text='Манговый унаги')
                bt_ris = types.KeyboardButton(text='Филадельфия классика')

                kb_rolls.add(bt_yd, bt_yd_2, bt_lapsh, bt_ris, bt_end)
                bot.send_message(id, f"""Вот что мы можем вам предложить:{n}""", reply_markup=kb_rolls)
                FLAG = 'continue_roll'
            else:
                bot.send_message(id, 'Прекрасный выбор!')
                bot.send_message(id, 'Как я могу к вам обращаться?', reply_markup=kb_skip)
                FLAG = 'continue_roll'

        if message.text.lower() == 'хочу вок':
            values = []
            kb_skip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_s = types.KeyboardButton(text='-поля для заполнения пользователем-')
            kb_skip.add(bt_s)

            if user_name:
                order.clear()

                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM wok""")
                data = cursor.fetchall()

                if message.text in values:
                    f = False
                    for i in order:
                        if i[0] == message.text:
                            cos = 0
                            for b in data:
                                if message.text == b[0]:
                                    cos = b[1]
                            order[order.index(i)][1] += 1
                            order[order.index(i)][2] = cos
                            print(i)
                            f = True

                    if not f:
                        cos = 0
                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order.append([message.text, 1, cos])
                    bot.send_message(id, 'Мы записали, что-то еще?')

                else:
                    if 'хочу' not in str(message.text.lower()).split():
                        bot.send_message(id, 'Такого блюда нет в наших списках.')
                n = ''

                for i in order:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'

                bot.send_message(id, 'Прекрасный выбор!')
                pic = open('brosh_pic/wok_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                kb_wok = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

                bt_yd = types.KeyboardButton(text='Удон с морепродуктами под китайским соусом')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_yd_2 = types.KeyboardButton(text='Удон с курицей под сливочным соусом')
                bt_lapsh = types.KeyboardButton(text='Лапша яичная с двойной курицей под соусом терияке')
                bt_ris = types.KeyboardButton(text='Рис с морепродуктами')

                kb_wok.add(bt_yd, bt_yd_2, bt_lapsh, bt_ris, bt_end)
                bot.send_message(id, f"""Вот что мы можем вам предложить:{n}""", reply_markup=kb_wok)
                FLAG = 'continue_wok'
            else:
                bot.send_message(id, 'Прекрасный выбор!')
                bot.send_message(id, 'Как я могу к вам обращаться?', reply_markup=kb_skip)
                FLAG = 'continue_wok'
            print('abaa')
        if message.text.lower() == 'хочу сет':
            print('asdasdasdasdasdasdas')
            values = []
            kb_skip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_s = types.KeyboardButton(text='-поля для заполнения пользователем-')
            kb_skip.add(bt_s)
            if user_name:
                order.clear()
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM [Set]""")
                data = cursor.fetchall()
                if message.text in values:
                    f = False
                    for i in order:
                        if i[0] == message.text:
                            cos = 0
                            for b in data:
                                if message.text == b[0]:
                                    cos = b[1]
                            order[order.index(i)][1] += 1
                            order[order.index(i)][2] = cos
                            print(i)
                            f = True

                    if not f:
                        cos = 0
                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order.append([message.text, 1, cos])
                    bot.send_message(id, 'Мы записали, что-то еще?')

                else:
                    if 'хочу' not in str(message.text.lower()).split():
                        bot.send_message(id, 'Такого блюда нет в наших списках.')
                n = ''

                for i in order:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'
                bot.send_message(id, 'Прекрасный выбор!')
                pic = open('brosh_pic/set_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                kb_set = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                bt_yd = types.KeyboardButton(text='Сет лайт кинг new')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_yd_2 = types.KeyboardButton(text='Сет филомания')
                bt_lapsh = types.KeyboardButton(text='Сет все будет хорошо new')
                bt_ris = types.KeyboardButton(text='Сет матерь драконов new')
                kb_set.add(bt_yd, bt_yd_2, bt_lapsh, bt_ris, bt_end)
                bot.send_message(id, f"""Вот что мы можем вам предложить:{n}""", reply_markup=kb_set)
                FLAG = 'continue_set'

            else:
                bot.send_message(id, 'Прекрасный выбор!')
                bot.send_message(id, 'Как я могу к вам обращаться?', reply_markup=kb_skip)
                FLAG = 'continue_set'
            print('aaaa')

        if message.text.lower() == 'хочу морс':
            values = []
            kb_skip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_s = types.KeyboardButton(text='-поля для заполнения пользователем-')
            kb_skip.add(bt_s)

            if user_name:
                order.clear()
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM juice""")
                data = cursor.fetchall()

                if message.text in values:
                    f = False
                    for i in order:
                        if i[0] == message.text:
                            cos = 0
                            for b in data:
                                if message.text == b[0]:
                                    cos = b[1]
                            order[order.index(i)][1] += 1
                            order[order.index(i)][2] = cos
                            print(i)
                            f = True

                    if not f:
                        cos = 0
                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order.append([message.text, 1, cos])
                    bot.send_message(id, 'Мы записали, что-то еще?')
                else:
                    if 'хочу' not in str(message.text.lower()).split():
                        bot.send_message(id, 'Такого блюда нет в наших списках.')
                n = ''

                for i in order:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'
                bot.send_message(id, 'Прекрасный выбор!')
                pic = open('brosh_pic/juice_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                kb_juic = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                bt_kl = types.KeyboardButton(text='Морс клюква')
                bt_brus = types.KeyboardButton(text='Морс брусника')
                bt_blc = types.KeyboardButton(text='Морс черная смородина')
                bt_obl = types.KeyboardButton(text='Морс облепиха-мед имбирь')
                bt_end = types.KeyboardButton(text='На этом все')
                kb_juic.add(bt_kl, bt_brus, bt_blc, bt_obl, bt_end)
                bot.send_message(id, f"""Вот что мы можем вам предложить:{n}""", reply_markup=kb_juic)
                FLAG = 'continue_juice'
            else:
                bot.send_message(id, 'Прекрасный выбор!')
                bot.send_message(id, 'Как я могу к вам обращаться?', reply_markup=kb_skip)
                FLAG = 'continue_juice'
            print('aaaa')
    elif FLAG == 'continue_roll':

        if not values:
            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name FROM rolls""")
            values = [i[0] for i in cursor.fetchall()]
            print(values)

        if message.text == '-поля для заполнения пользователем-':
            bot.send_message(id, 'Введите данные вручную.')

        elif message.text.lower() == 'да':
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

        elif message.text.lower() == 'на этом все':
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            bt_yes = types.KeyboardButton(text='Да, все верно')
            bt_not = types.KeyboardButton(text='Изменить')
            kb.add(bt_yes, bt_not)
            count = 0
            n = ''

            for i in order:
                n += f'\n🔻 {i[0]} \n Количество:    {i[1]}шт.\n За {i[1]}шт.: {i[2] * i[1]}₽\n'
                count += i[2] * i[1]
            stri = f"""Прекрасно! Что же у нас в корзине?
_____________
{n}

Итого к оплате:  {count} руб.

_____________

Оформить заказ ? Он будет сразу передан на кухню !😃"""
            bot.send_message(id, stri, reply_markup=kb)
            bot.send_message(id, "Если вы есть в нашкй бонусной системе, "
                                 "то после получения заказа мы зачислим вам 5% бонусных рублей от стоимости заказа!")

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT user_id,
                   phone_number,
                   name_pers,
                   balance
              FROM users WHERE user_id == '{id}';""")
            data = cursor.fetchall()

            if not data:
                bot.send_message(message.chat.id, 'Вы не учавствуете в системе.\n'
                                                  'Сделайте 1 заказ, чтобы стать участником системы')
            else:
                bot.send_message(message.chat.id, f'Вы уже учавствуете в системе бонусов.\nВаше имя: {data[0][2]}\n'
                                                  f'Ваш номер телефона: {data[0][1]}\n'
                                                  f'Ваш баланс: {data[0][3]}')
                bonus = round((count * 1.05) - count)
                bot.send_message(id, f'После получения данного заказа вам будет начисленно: {bonus} руб.')
                b = data[0][3] + bonus
                cursor.execute(f"""
DELETE FROM users WHERE user_id = {id}
""")
                cursor.execute(f"""
INSERT INTO users (
                      user_id,
                      phone_number,
                      name_pers,
                      balance
                  )
                  VALUES (
                      {id},
                      'phone_number',
                      'name_pers',
                      {b}
                  );
""")
                connect.commit()
            FLAG = 'continue_oform'

        elif not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.capitalize()}, введите ваш номер телефона')

        elif user_name and not number_phone:
            if check_num(message.text):
                kb_rolls = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                bt_yd = types.KeyboardButton(text='Ролл Фудзи')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_yd_2 = types.KeyboardButton(text='Калифорния сяке с икрой')
                bt_lapsh = types.KeyboardButton(text='Манговый унаги')
                bt_ris = types.KeyboardButton(text='Филадельфия классика')
                kb_rolls.add(bt_yd, bt_yd_2, bt_lapsh, bt_ris, bt_end)
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM rolls""")
                data = cursor.fetchall()
                print(data)
                n = ''

                for i in data:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'
                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                pic = open('brosh_pic/rolls_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                bot.send_message(id, f"""Вот что мы можем вам предложить:
{n}""", reply_markup=kb_rolls)
                number_phone = message.text
            else:
                bot.send_message(id, 'Номер некорректен...')
        elif user_name and number_phone and cont_order:

            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name, cost, count FROM rolls""")
            data = cursor.fetchall()

            if message.text in values:
                f = False

                for i in order:
                    if i[0] == message.text:
                        cos = 0

                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order[order.index(i)][1] += 1
                        order[order.index(i)][2] = cos
                        print(i)
                        f = True
                if not f:
                    cos = 0

                    for b in data:
                        if message.text == b[0]:
                            cos = b[1]
                    order.append([message.text, 1, cos])
                bot.send_message(id, 'Мы записали, что-то еще?')
            else:
                bot.send_message(id, 'Такого блюда нет в наших списках.')

    elif FLAG == 'continue_wok':

        if not values:
            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name FROM wok""")
            values = [i[0] for i in cursor.fetchall()]
            print(values)

        if message.text == '-поля для заполнения пользователем-':
            bot.send_message(id, 'Введите данные вручную.')

        elif message.text.lower() == 'да':
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

        elif message.text.lower() == 'на этом все':

            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            bt_yes = types.KeyboardButton(text='Да, все верно')
            bt_not = types.KeyboardButton(text='Изменить')
            kb.add(bt_yes, bt_not)
            count = 0
            n = ''
            for i in order:
                n += f'\n🔻 {i[0]} \n Количество:    {i[1]}шт.\n За {i[1]}шт.: {i[2] * i[1]}₽\n'
                count += i[2] * i[1]
            stri = f"""Прекрасно! Что же у нас в корзине?
 _____________
        {n}

Итого к оплате:  {count} руб.

_____________

Оформить заказ ? Он будет сразу передан на кухню !😃"""
            bot.send_message(id, stri, reply_markup=kb)
            bot.send_message(id, "Если вы есть в нашкй бонусной системе, "
                                 "то после получения заказа мы зачислим вам 5% бонусных рублей от стоимости заказа!")

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT user_id,
                               phone_number,
                               name_pers,
                               balance
                          FROM users WHERE user_id == '{id}';""")
            data = cursor.fetchall()

            if not data:
                bot.send_message(message.chat.id, 'Вы не учавствуете в системе.\n'
                                                  'Сделайте 1 заказ, чтобы стать участником системы')
            else:
                bot.send_message(message.chat.id, f'Вы уже учавствуете в системе бонусов.\nВаше имя: {data[0][2]}\n'
                                                  f'Ваш номер телефона: {data[0][1]}\n'
                                                  f'Ваш баланс: {data[0][3]}')
                bonus = round((count * 1.05) - count)
                bot.send_message(id, f'После получения данного заказа вам будет начисленно: {bonus} руб.')
                b = data[0][3] + bonus
                cursor.execute(f"""
                DELETE FROM users WHERE user_id = {id}
                """)
                cursor.execute(f"""
                INSERT INTO users (
                                      user_id,
                                      phone_number,
                                      name_pers,
                                      balance
                                  )
                                  VALUES (
                                      {id},
                                      'phone_number',
                                      'name_pers',
                                      {b}
                                  );
                """)
                connect.commit()
            FLAG = 'continue_oform'

        elif not user_name:

            user_name = message.text
            bot.send_message(id, f'{user_name.capitalize()}, введите ваш номер телефона')

        elif user_name and not number_phone:

            if check_num(message.text):
                kb_wok = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

                bt_yd = types.KeyboardButton(text='Удон с морепродуктами под китайским соусом')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_yd_2 = types.KeyboardButton(text='Удон с курицей под сливочным соусом')
                bt_lapsh = types.KeyboardButton(text='Лапша яичная с двойной курицей под соусом терияке')
                bt_ris = types.KeyboardButton(text='Рис с морепродуктами')

                kb_wok.add(bt_yd, bt_yd_2, bt_lapsh, bt_ris, bt_end)
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM wok""")
                data = cursor.fetchall()
                print(data)
                n = ''

                for i in data:

                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'
                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                pic = open('brosh_pic/wok_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                bot.send_message(id, f"""Вот что мы можем вам предложить:
        {n}""", reply_markup=kb_wok)
                number_phone = message.text

            else:
                bot.send_message(id, 'Номер некорректен...')

        elif user_name and number_phone and cont_order:

            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name, cost, count FROM wok""")
            data = cursor.fetchall()
            if message.text in values:
                f = False

                for i in order:
                    if i[0] == message.text:
                        cos = 0
                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order[order.index(i)][1] += 1
                        order[order.index(i)][2] = cos
                        print(i)
                        f = True

                if not f:
                    cos = 0
                    for b in data:
                        if message.text == b[0]:
                            cos = b[1]
                    order.append([message.text, 1, cos])
                bot.send_message(id, 'Мы записали, что-то еще?')

            else:
                bot.send_message(id, 'Такого блюда нет в наших списках.')

    elif FLAG == 'continue_set':

        if not values:
            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name FROM [Set]""")
            values = [i[0] for i in cursor.fetchall()]
            print(values)

        if message.text == '-поля для заполнения пользователем-':
            bot.send_message(id, 'Введите данные вручную.')

        elif message.text.lower() == 'да':

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

        elif message.text.lower() == 'на этом все':
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            bt_yes = types.KeyboardButton(text='Да, все верно')
            bt_not = types.KeyboardButton(text='Изменить')
            kb.add(bt_yes, bt_not)
            count = 0
            n = ''

            for i in order:
                n += f'\n🔻 {i[0]} \n Количество:    {i[1]}шт.\n За {i[1]}шт.: {i[2] * i[1]}₽\n'
                count += i[2] * i[1]
            stri = f"""Прекрасно! Что же у нас в корзине?
_____________
{n}

Итого к оплате:  {count} руб.

_____________

Оформить заказ ? Он будет сразу передан на кухню !😃"""
            bot.send_message(id, stri, reply_markup=kb)
            bot.send_message(id, "Если вы есть в нашкй бонусной системе, "
                                 "то после получения заказа мы зачислим вам 5% бонусных рублей от стоимости заказа!")

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT user_id,
                               phone_number,
                               name_pers,
                               balance
                          FROM users WHERE user_id == '{id}';""")
            data = cursor.fetchall()

            if not data:
                bot.send_message(message.chat.id, 'Вы не учавствуете в системе.\n'
                                                  'Сделайте 1 заказ, чтобы стать участником системы')
            else:
                bot.send_message(message.chat.id, f'Вы уже учавствуете в системе бонусов.\nВаше имя: {data[0][2]}\n'
                                                  f'Ваш номер телефона: {data[0][1]}\n'
                                                  f'Ваш баланс: {data[0][3]}')
                bonus = round((count * 1.05) - count)
                bot.send_message(id, f'После получения данного заказа вам будет начисленно: {bonus} руб.')
                b = data[0][3] + bonus
                cursor.execute(f"""
                DELETE FROM users WHERE user_id = {id}
                """)
                cursor.execute(f"""
                INSERT INTO users (
                                      user_id,
                                      phone_number,
                                      name_pers,
                                      balance
                                  )
                                  VALUES (
                                      {id},
                                      'phone_number',
                                      'name_pers',
                                      {b}
                                  );
                """)
                connect.commit()
                connect.commit()
            FLAG = 'continue_oform'

        elif not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.capitalize()}, введите ваш номер телефона')

        elif user_name and not number_phone:

            if check_num(message.text):

                kb_set = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

                bt_yd = types.KeyboardButton(text='Сет лайт кинг new')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_yd_2 = types.KeyboardButton(text='Сет филомания')
                bt_lapsh = types.KeyboardButton(text='Сет все будет хорошо new')
                bt_ris = types.KeyboardButton(text='Сет матерь драконов new')

                kb_set.add(bt_yd, bt_yd_2, bt_lapsh, bt_ris, bt_end)
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM [Set]""")
                data = cursor.fetchall()
                print(data)
                n = ''

                for i in data:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'

                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                pic = open('brosh_pic/set_pic.jpg', 'rb')
                bot.send_photo(id, pic)
                bot.send_message(id, f"""Вот что мы можем вам предложить:
        {n}""", reply_markup=kb_set)
                number_phone = message.text

            else:
                bot.send_message(id, 'Номер некорректен...')

        elif user_name and number_phone and cont_order:
            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name, cost, count FROM [Set]""")
            data = cursor.fetchall()

            if message.text in values:
                f = False

                for i in order:
                    if i[0] == message.text:
                        cos = 0

                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order[order.index(i)][1] += 1
                        order[order.index(i)][2] = cos
                        print(i)
                        f = True

                if not f:
                    cos = 0
                    for b in data:
                        if message.text == b[0]:
                            cos = b[1]
                    order.append([message.text, 1, cos])
                bot.send_message(id, 'Мы записали, что-то еще?')

            else:
                bot.send_message(id, 'Такого блюда нет в наших списках.')

    elif FLAG == 'continue_juice':

        if not values:
            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name FROM juice""")
            values = [i[0] for i in cursor.fetchall()]
            print(values)

        if message.text == '-поля для заполнения пользователем-':
            bot.send_message(id, 'Введите данные вручную.')

        elif message.text.lower() == 'да':
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_rolls = types.KeyboardButton(text='Хочу роллы')
            bt_wok = types.KeyboardButton(text='Хочу вок')
            bt_set = types.KeyboardButton(text='Хочу сет')
            bt_ju = types.KeyboardButton(text='Хочу морс')
            kb.add(bt_set, bt_rolls, bt_wok, bt_ju)

            bot.send_message(id, '''Приветсвую вас! Я бот-помощник компании Yandex Sushi
Мы рады приветсвовать вас!
Для заказа роллов напишите: "Хочу роллы"
Для заказа вока напишите: "Хочу вок"
Для заказа наборов суши напишите: "Хочу сет"
Для заказа напитков: "Хочу морс"
''', reply_markup=kb)
            FLAG = 'continue_start'

        elif message.text.lower() == 'на этом все':
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            bt_yes = types.KeyboardButton(text='Да, все верно')
            bt_not = types.KeyboardButton(text='Изменить')
            kb.add(bt_yes, bt_not)
            count = 0
            n = ''

            for i in order:
                n += f'\n🔻 {i[0]} \n Количество:    {i[1]}шт.\n За {i[1]}шт.: {i[2] * i[1]}₽\n'
                count += i[2] * i[1]
            stri = f"""Прекрасно! Что же у нас в корзине?
_____________
{n}

Итого к оплате:  {count} руб.

_____________

Оформить заказ ? Он будет сразу передан на кухню !😃"""
            bot.send_message(id, stri, reply_markup=kb)
            bot.send_message(id, "Если вы есть в нашкй бонусной системе, "
                                 "то после получения заказа мы зачислим вам 5% бонусных рублей от стоимости заказа!")

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT user_id,
                                           phone_number,
                                           name_pers,
                                           balance
                                      FROM users WHERE user_id == '{id}';""")
            data = cursor.fetchall()

            if not data:
                bot.send_message(message.chat.id, 'Вы не учавствуете в системе.\n'
                                                  'Сделайте 1 заказ, чтобы стать участником системы')
            else:
                bot.send_message(message.chat.id, f'Вы уже учавствуете в системе бонусов.\nВаше имя: {data[0][2]}\n'
                                                  f'Ваш номер телефона: {data[0][1]}\n'
                                                  f'Ваш баланс: {data[0][3]}')
                bonus = round((count * 1.05) - count)
                bot.send_message(id, f'После получения данного заказа вам будет начисленно: {bonus} руб.')
                b = data[0][3] + bonus
                cursor.execute(f"""
                            DELETE FROM users WHERE user_id = {id}
                            """)
                cursor.execute(f"""
                            INSERT INTO users (
                                                  user_id,
                                                  phone_number,
                                                  name_pers,
                                                  balance
                                              )
                                              VALUES (
                                                  {id},
                                                  'phone_number',
                                                  'name_pers',
                                                  {b}
                                              );
                            """)
                connect.commit()
            FLAG = 'continue_oform'

        elif not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.capitalize()}, введите ваш номер телефона')

        elif user_name and not number_phone:

            if check_num(message.text):
                kb_juic = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

                # наши напитки в меню
                bt_kl = types.KeyboardButton(text='Морс клюква')
                bt_brus = types.KeyboardButton(text='Морс брусника')
                bt_blc = types.KeyboardButton(text='Морс черная смородина')
                bt_obl = types.KeyboardButton(text='Морс облепиха-мед имбирь')
                bt_end = types.KeyboardButton(text='На этом все')
                kb_juic.add(bt_kl, bt_brus, bt_blc, bt_obl, bt_end)
                connect = sqlite3.connect('eat.db')
                cursor = connect.cursor()
                cursor.execute(f"""SELECT name, cost, count FROM juice""")
                data = cursor.fetchall()
                print(data)
                n = ''

                for i in data:
                    if i:
                        n += f'\n🔻{i[0]}\n Цена:    {i[1]}₽\n Количество в наборе: {i[2]}шт.\n'
                bot.send_message(id, 'Хорошо, что бы вы хотели заказать?')
                pic = open('brosh_pic/juice_pic.jpg', 'rb')
                bot.send_photo(id, pic)

                # напоминание о наших предложениях
                bot.send_message(id, f"""Вот что мы можем вам предложить:
            {n}""", reply_markup=kb_juic)
                number_phone = message.text

            else:
                bot.send_message(id, 'Номер некорректен...')

        elif user_name and number_phone and cont_order:
            connect = sqlite3.connect('eat.db')
            cursor = connect.cursor()
            cursor.execute(f"""SELECT name, cost, count FROM juice""")
            data = cursor.fetchall()

            if message.text in values:
                f = False

                for i in order:
                    if i[0] == message.text:
                        cos = 0

                        for b in data:
                            if message.text == b[0]:
                                cos = b[1]
                        order[order.index(i)][1] += 1
                        order[order.index(i)][2] = cos
                        print(i)
                        f = True

                if not f:
                    cos = 0
                    for b in data:
                        if message.text == b[0]:
                            cos = b[1]
                    order.append([message.text, 1, cos])
                bot.send_message(id, 'Мы записали, что-то еще?')

            else:
                bot.send_message(id, 'Такого блюда нет в наших списках.')

    elif FLAG == '':
        pass

    else:
        bot.send_message(id, 'Я не понял вашу команду...')
        user_name = message.text


if __name__ == '__main__':
    bot.polling(none_stop=True)