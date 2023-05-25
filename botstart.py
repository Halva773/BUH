from threading import Thread
from time import sleep

import schedule
import telebot
from dadata import Dadata
from telebot import types

import database
import operations
from creds import DaDataToken, telebot_token
from gmailAPI import check_email

dadata = Dadata(DaDataToken)
bot = telebot.TeleBot(telebot_token)

newUser = {'fio': None,
           'id': None}
userDict = {"group_name": None,
            "admin_name": None}
print("[START] Бот запущен")


@bot.message_handler(commands=["start"])
def start(message):
    if database.find_group_with_id(message.chat.id) == False:
        # Клавиатура с кнопкой запроса локации
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_reg = types.KeyboardButton(text="Создать группу")
        button_sing = types.KeyboardButton(text="Найти группу")
        keyboard.add(button_reg, button_sing)
        msg = bot.send_message(message.chat.id, "Привет!!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, buttonsCheck)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение",
                                          request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id,
                         "Вы уже зарегестрированы в системе и не можете находитсья в более, чем 1 группе",
                         reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def buttonsCheck(message):
    global newUser
    print(f"[MESSAGE] {message.text}")
    if message.text == "Создать группу":
        print("[INFO] Create Group")
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id, 'Название группы?', reply_markup=markup)
        bot.register_next_step_handler(msg, fio)
    elif message.text == "Найти группу":
        markup = telebot.types.ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, "Напишите своё ФИО", reply_markup=markup)
        bot.register_next_step_handler(msg, userAuth)
    elif message.text == "Да, всё верно":
        generateID = operations.generateID()
        groupid = next(generateID)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение",
                                          request_location=True)
        keyboard.add(button_geo)
        database.create_group(userDict['group_name'], groupid, message.chat.id, userDict['admin_name'])
        bot.send_message(message.from_user.id, f"Группа {userDict['group_name']} успешно создана\nID вашей группы: "
                                               f"{groupid}\nИспользуйте этот ID для добавления других пользователей",
                         reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def fio(message):
    userDict['group_name'] = message.text.replace("-", "_")
    msg = bot.send_message(message.from_user.id, "Напишите ФИО")
    bot.register_next_step_handler(msg, finish_registration)


@bot.message_handler(content_types=['text'])
def finish_registration(message):
    userDict["admin_name"] = message.text
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_yes = types.KeyboardButton(text="Да, всё верно")
    button_no = types.KeyboardButton(text="Нет, не верно")
    keyboard.add(button_yes, button_no)
    bot.send_message(message.from_user.id,
                     f"Проверьте правильность введённых данны:\nИмя группы: {userDict['group_name']}"
                     f"\nВаше фио: {userDict['admin_name']}\nВсё верно?", reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        lat = message.location.latitude
        lon = message.location.longitude
        location = dadata.geolocate(name="address", lat=lat, lon=lon, radius_meters=50)
        if operations.checkLocation(location):
            usermessage = "✅ Вас отметили"
            database.update_date(database.find_group_with_id(message.chat.id), message.chat.id)
        else:
            usermessage = "❌ К сожалению мы не зафиксировали ваше местоположение в финансовом университете"
        bot.send_message(message.chat.id, usermessage)


@bot.message_handler(content_types=['text'])
def userAuth(message):
    global newUser
    newUser['fio'] = message.text
    msg = bot.send_message(message.chat.id, "Введите ID группы")
    bot.register_next_step_handler(msg, groupSearch)


@bot.message_handler(content_types=['text'])
def groupSearch(message):
    global newUser
    try:
        group = database.searchGroupData(message.text)[0]
        group['admin_id'] = database.searchAdminData(group['group_name'])[0]['id']
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        database.join_user(message.from_user.id, newUser['fio'], group['group_name'], 'req')
        acceptButton = types.InlineKeyboardButton(text="Принять ✅",
                                                  callback_data=str({'action': '1',
                                                                     'group_id': message.text,
                                                                     'user': message.from_user.id}))
        denyButton = types.InlineKeyboardButton(text="Отклонить ❌",
                                                callback_data=str({'action': '0',
                                                                   'group_id': message.text,
                                                                   'user': message.from_user.id}))
        keyboard.add(acceptButton, denyButton)
        bot.send_message(group['admin_id'],
                         f"Пользователь {newUser['fio']} запрашивает вход в группу", reply_markup=keyboard)
        bot.send_message(message.from_user.id,
                         f"Группа {group['group_name']} найдена. Заявка на вступление отправлена администратору группы")
    except IndexError:
        bot.send_message(message.from_user.id, "Группа с таким ID не найдена")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data:
        data = eval(call.data)
        group = database.searchGroupData(data['group_id'])[0]
        database.response_handler(data['action'], group['group_name'], data['user'])
        print(data)
        if data['action'] == "1":
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_geo = types.KeyboardButton(text="Доброе утро, отправь мне свое местоположение",
                                              request_location=True)
            keyboard.add(button_geo)
            bot.send_message(data['user'], f'Запрос на вступление в группу {group["group_name"]} принят!',
                             reply_markup=keyboard)
        else:
            bot.send_message(data['user'], f'Запрос на вступление в группу {group["group_name"]} был отклонён')


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def function_to_run(lesson_number):
    return bot.send_message(968913533, operations.get_student_list(968913533, lesson_number))


def send_message(id, message):
    bot.send_message(id, message)


def req_for_check_email():
    print("Проверка почты")
    users = database.get_time_of_group_members(database.find_group_with_id(968913533))
    users_ids = []
    for user in users:
        users_ids.append(user['id'])
    check_email(users_ids)


if __name__ == '__main__':
    schedule.every().day.at("09:45").do(function_to_run, lesson_number=1)
    schedule.every().day.at("11:25").do(function_to_run, lesson_number=2)
    schedule.every().day.at("13:05").do(function_to_run, lesson_number=3)
    schedule.every().day.at("15:15").do(function_to_run, lesson_number=4)
    schedule.every().day.at("17:35").do(function_to_run, lesson_number=5)
    schedule.every().day.at("18:35").do(function_to_run, lesson_number=6)
    schedule.every().day.at("20:20").do(function_to_run, lesson_number=7)
    schedule.every(30).minutes.do(req_for_check_email)
    Thread(target=schedule_checker).start()

    bot.polling()
