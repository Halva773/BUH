from datetime import datetime
from prettytable import PrettyTable

import database

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


def get_student_list(admin_id, current_lesson):
    result = []
    lessons_time = [94500, 112500, 130500, 151500, 165500, 183500]
    group_name = database.find_group_with_id(admin_id)
    users = database.get_time_of_group_members(group_name)
    current_datetime = datetime.now()
    current_date = f"{current_datetime.day}-{current_datetime.month}-{current_datetime.year}"
    for user in users:
        user_date = user['last_join_time'].split(' ')[0]
        user_time = int("".join(user['last_join_time'].split(' ')[1].split(":")))
        if user_date == current_date and lessons_time[current_lesson - 2] < user_time < lessons_time[current_lesson - 1]:
            result.append(user['student_name'])
    return generate_message(result, current_lesson, group_name)


def generate_message(noted, current_lesson, group_name):
    header = ['ФИО', 'Отметка']
    name = []
    if len(noted) < 1:
        pass
    msg = f"Номер пары: {current_lesson}\nФИО\t\tОтметка\n"
    users = database.get_time_of_group_members(group_name)
    for user in users:
        fio = user['student_name'].split()
        name.append('*' if user['student_name'] in noted else "н")
        name.append(f"{fio[0]} {fio[1]}")


    columns = len(header)
    table = PrettyTable(header)
    name_data = name[:]
    while name_data:
        table.add_row(name_data[:columns])
        name_data = name_data[columns:]
    print(table, type(table))
    return str(table)


    table = PrettyTable(name)
    columns = len(name)
    name_data = name[:]
    while name_data:
        table.add_row(name_data[:columns])
        name_data = name_data[:columns]
    print(table, type(table))
    return str(table)


def get_current_time():
    current_datetime = datetime.now()
    time = [str(current_datetime.hour), str(current_datetime.minute), str(current_datetime.second)]
    for item in range(len(time)):
        if len(time[item]) < 2:
            time[item] = "0" + time[item]
    current_time = f"{current_datetime.day}-{current_datetime.month}-{current_datetime.year} {time[0]}:{time[1]}:{time[2]}"
    return current_time


if __name__ == '__main__':
    print(get_current_time())
    # get_student_list(968913533)
