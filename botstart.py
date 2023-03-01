import telebot
from telebot import types
from dadata import Dadata
from operations import checkLocation
from creds import DaDataToken, telebot_token


dadata = Dadata(DaDataToken)
bot = telebot.TeleBot(telebot_token)


@bot.message_handler(commands=["geo"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение", reply_markup=keyboard)

@bot.message_handler(commands=["start"])
def start (message):
    #Клавиатура с кнопкой запроса локации
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_reg = types.KeyboardButton(text="Создать группу")
    button_sing = types.KeyboardButton(text="Найти группу")
    keyboard.add(button_reg, button_sing)
    bot.send_message(message.chat.id, "Поделись местоположением", reply_markup=keyboard)
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
        if checkLocation(location):
            usermessage += "Ты чё в телеге сидишь? Иди ботай!"
        bot.send_message(message.chat.id, f"Your possible locations is:\n{usermessage}")

bot.polling(none_stop = True)
input()

#968913533 - артем