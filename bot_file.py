import config
import sqlite3
import telebot
import re
from telebot import types


FLAG = ''
status_bar = ''
cont_order = True
values = []


def check_num(string):
    phone = re.sub(r'\b\D', '', string)
    clear_phone = re.sub(r'[\ \(]?', '', phone)
    if re.findall(r'^[\+7|8]*?\d{10}$', clear_phone) or re.match(r'^\w+[\.]?(\w+)*\@(\w+\.)*\w{2,}$',string):
        return True
    else: return False


bot = telebot.TeleBot(config.TOKEN)
user_name, number_phone, order = '', '', []


@bot.message_handler(commands=['start'])
def start(message):
    global FLAG
    id = message.chat.id
    if FLAG == '':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        bt_rolls = types.KeyboardButton(text='Хочу роллы')
        bt_wok = types.KeyboardButton(text='Хочу вок')
        bt_set = types.KeyboardButton(text='Хочу сет')
        kb.add(bt_set, bt_rolls, bt_wok)

        bot.send_message(id, '''Добрый день ! 😃 
    Я - бот-помощник(Yandex Sushi)
    Я могу вас предоставить:
    •роллы
    •вок
    •сет
    Для заказа напишите ,,Хочу …(выбранное вами блюдо)’’
                                 ''', reply_markup=kb)
        FLAG = 'continue_start'


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


'''@bot.message_handler(content_types=['text'])
def hello(msg):
    global FLAG
    id = msg.chat.id
    if FLAG == '':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        bt_rolls = types.KeyboardButton(text='Хочу роллы')
        bt_wok = types.KeyboardButton(text='Хочу вок')
        bt_set = types.KeyboardButton(text='Хочу сет')
        kb.add(bt_set, bt_rolls, bt_wok)


        FLAG = 'continue_start'
    elif FLAG == 'continue start':
        pass
    elif FLAG == 'continue_roll':
        kb_rolls = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        bt_fudz = types.KeyboardButton(text='Ролл Фудзи')
        bt_kalif = types.KeyboardButton(text='Калифорния сяке с икрой')
        bt_ung = types.KeyboardButton(text='Манговый унаги')
        bt_filad = types.KeyboardButton(text='Филадельфия классика')
        kb_rolls.add(bt_fudz, bt_kalif, bt_ung, bt_filad)'''


@bot.message_handler(content_types=['text'])
def get_text(message):
    global user_name, number_phone, order, FLAG, values
    id = message.chat.id
    if FLAG == '':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        bt_rolls = types.KeyboardButton(text='Хочу роллы')
        bt_wok = types.KeyboardButton(text='Хочу вок')
        bt_set = types.KeyboardButton(text='Хочу сет')
        kb.add(bt_set, bt_rolls, bt_wok)

        bot.send_message(id, '''Добрый день ! 😃 
Я - бот-помощник(Yandex Sushi)
Я могу вас предоставить:
•роллы
•вок
•сет
Для заказа напишите ,,Хочу …(выбранное вами блюдо)’’
                             ''', reply_markup=kb)
        FLAG = 'continue_start'
    elif FLAG == 'continue_oform':
        kb_start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        bt_start = types.KeyboardButton(text='/start')
        kb_start.add(bt_start)
        kbb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        bt_yes = types.KeyboardButton(text='Да, хочу!')
        bt_not = types.KeyboardButton(text='Увы, нет')
        kbb.add(bt_yes, bt_not)
        n = ''
        for i in order:
            n += f'{i[0]} - {i[1]}x\n'
        if message.text.lower() == 'да, все верно':
            strin = f"""!СПАСИБО ЗА ЗАКАЗ!
Ваш заказ:
{n} Заказ находится в обработке, ожидайте связи с оператором по вышеуказанному номеру!"""
            bot.send_message(id, strin)
            bot.send_message(id, 'Вы совершили 1 заказ в нашем магазине! '
                                 'Вы хотите учавствовать в бонусной системе нашего ресторана?',
                             reply_markup=kbb)
        elif message.text.lower() == 'да, хочу!':
            bot.send_message(id, '/add')
        elif message.text.lower() == 'увы, нет':
            bot.send_message(id, 'Очень жаль =(\nСпасибо за заказ!', reply_markup=kb_start)
            FLAG = ''
        elif message.text == 'Нет':
            bot.send_message(id, 'Хорошо, мы отменили вашу заявку, спасибо за выбор нашего сервиса!')

    elif FLAG == 'continue_start':
        if message.text.lower() == 'хочу роллы':
            kb_skip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            bt_s = types.KeyboardButton(text='-поля для заполнения пользователем-')
            kb_skip.add(bt_s)
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
                kb_rolls = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                bt_fudz = types.KeyboardButton(text='Ролл Фудзи')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_kalif = types.KeyboardButton(text='Калифорния сяке с икрой')
                bt_ung = types.KeyboardButton(text='Манговый унаги')
                bt_filad = types.KeyboardButton(text='Филадельфия классика')
                kb_rolls.add(bt_fudz, bt_kalif, bt_ung, bt_filad, bt_end)
                bot.send_message(id, f"""Вот что мы можем вам предложить:{n}""", reply_markup=kb_rolls)
                FLAG = 'continue_roll'
            else:
                bot.send_message(id, 'Прекрасный выбор!')
                bot.send_message(id, 'Как я могу к вам обращаться?', reply_markup=kb_skip)
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
            bt_not = types.KeyboardButton(text='Увы, нет')
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
            FLAG = 'continue_oform'
        elif not user_name:
            user_name = message.text
            bot.send_message(id, f'{user_name.capitalize()}, введите ваш номер телефона')
        elif user_name and not number_phone:
            if check_num(message.text):
                kb_rolls = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                bt_fudz = types.KeyboardButton(text='Ролл Фудзи')
                bt_end = types.KeyboardButton(text='На этом все')
                bt_kalif = types.KeyboardButton(text='Калифорния сяке с икрой')
                bt_ung = types.KeyboardButton(text='Манговый унаги')
                bt_filad = types.KeyboardButton(text='Филадельфия классика')
                kb_rolls.add(bt_fudz, bt_kalif, bt_ung, bt_filad, bt_end)
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
                        order[order.index(i)][2] += cos
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