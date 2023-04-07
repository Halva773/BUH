import telebot
from dadata import Dadata
from telebot import types

import database
import operations
from creds import DaDataToken, telebot_token

dadata = Dadata(DaDataToken)
bot = telebot.TeleBot(telebot_token)

newUser = {'fio': None,
           'id': None}
userDict = {"group_name": None,
            "admin_name": None}
print("[START] Бот запущен")


@bot.message_handler(commands=["geo"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение",
                     reply_markup=keyboard)


@bot.message_handler(commands=["start"])
def start(message):
    # Клавиатура с кнопкой запроса локации
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_reg = types.KeyboardButton(text="Создать группу")
    button_sing = types.KeyboardButton(text="Найти группу")
    keyboard.add(button_reg, button_sing)
    msg = bot.send_message(message.chat.id, "Привет!!", reply_markup=keyboard)
    bot.register_next_step_handler(msg, buttonsCheck)


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
        msg = bot.send_message(message.chat.id, "Напишите своё ФИО")
        bot.register_next_step_handler(msg, userAuth)
    elif message.text == "Да, всё верно":
        generateID = operations.generateID()
        groupid = next(generateID)
        database.create_group(userDict['group_name'], groupid, message.chat.id, userDict['admin_name'])
        bot.send_message(message.from_user.id, f"Группа {userDict['group_name']} успешно создана\nID вашей группы: "
                                               f"{groupid}\nИспользуйте этот ID для добавления других пользователей")


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
    usermessage = ''
    if message.location is not None:
        print(message.location)
        lat = message.location.latitude
        lon = message.location.longitude
        location = dadata.geolocate(name="address", lat=lat, lon=lon, radius_meters=50)
        for loc in location:
            usermessage += loc['value'] + "\n"
        print(usermessage)
        if operations.checkLocation(location):
            usermessage += "Ты чё в телеге сидишь? Иди ботай!"
        bot.send_message(message.chat.id, f"Your possible locations is:\n{usermessage}")


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
        print(data)
        group = database.searchGroupData(data['group_id'])[0]
        database.response_handler(data['action'], group['group_name'], data['user'])
        print(data)
        if data['action'] == "1":
            bot.send_message(data['user'][0], f'Запрос на вступление в группу {group["group_name"]} принят!')
        else:
            bot.send_message(data['user'][0], f'Запрос на вступление в группу {group["group_name"]} был отклонён')


bot.polling(none_stop=True)
input()
