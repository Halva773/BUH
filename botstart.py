import telebot
from dadata import Dadata
from telebot import types

import database
import operations
from creds import DaDataToken, telebot_token

dadata = Dadata(DaDataToken)
bot = telebot.TeleBot(telebot_token)
userDict = {"group_name": None,
            "admin_name": None}
print("Бот запущен")


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
    if message.text == "Создать группу":
        print("[INFO] Create Group")
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id, 'Название группы?', reply_markup=markup)
        bot.register_next_step_handler(msg, fio)
    elif message.text == "Найти группу":
        bot.send_message(message.chat.id, "Вы пытаетесь найти группу")
    elif message.text == "Да, всё верно":
        groupid = operations.generateID()
        admin_id = int(message.chat.id)
        database.create_group(userDict['group_name'], next(groupid), admin_id)
        bot.send_message(message.fron_user.id, f"Группа {userDict['group_name']} успешно создана\nID вашей группы: "
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


bot.polling(none_stop=True)
input()
