from datetime import datetime

print("[START] Файл operations.py запущен")


def checkLocation(location):
    for loc in location:
        if "4-й Вешняковский проезд, д 4" in loc['value']:
            return True
    return False


def generateID():
    i = 2
    while True:
        i += 1
        yield i


def get_current_time():
    current_datetime = datetime.now()
    current_time = f"{current_datetime.day}-{current_datetime.month}-{current_datetime.year} {current_datetime.hour}:{current_datetime.minute}:{current_datetime.second}"
    return current_time
