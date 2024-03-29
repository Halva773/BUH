import pymysql.cursors

from creds import password, user
from operations import get_current_time



def table_connect():
    connections = pymysql.connect(
        host="localhost",
        port=3306,
        user=user,
        db="BUH",
        password=password,
        cursorclass=pymysql.cursors.DictCursor)
    return connections


def create_group(group_name, group_id, admin_id, admin_name):
    connection = table_connect()
    with connection.cursor() as cursor:
        sql = f"CREATE table IF NOT EXISTS {group_name} (id BIGINT UNSIGNED PRIMARY KEY, student_name VARCHAR(50), status VARCHAR(10), last_join_time VARCHAR(20));"
        cursor.execute(sql)
        sql = f"INSERT INTO {group_name} (id, student_name, status, last_join_time) values (%s, %s, %s, %s)"
        cursor.execute(sql, (admin_id, admin_name, "owner", get_current_time()))
        sql = f"INSERT INTO groups_ids (group_id, group_name) values (%s, %s)"
        cursor.execute(sql, (group_id, group_name))
        connection.commit()
    return "200"


def join_user(id, student_name, group, status):
    connections = table_connect()
    with connections.cursor() as cursor:
        sql = f"INSERT INTO {group} (id, student_name, status, last_join_time) values (%s, %s, %s, %s);"
        cursor.execute(sql, (id, student_name, status, get_current_time()))
        connections.commit()
    return "200"


def response_handler(action, group_name, user_id):
    connections = table_connect()
    with connections.cursor() as cursor:
        if action:
            sql = f"update {group_name} set status = 'member' where id = {user_id}"
        else:
            sql = f"delete {group_name} where id = {user_id}"
        cursor.execute(sql)
        connections.commit()
    return "200"


def searchGroupData(group_id):
    connections = table_connect()
    with connections.cursor() as cursor:
        request = f"SELECT * FROM groups_ids WHERE group_id = {group_id}"
        cursor.execute(request)
        result = cursor.fetchall()
        return result


def searchAdminData(group_name):
    connections = table_connect()
    with connections.cursor() as cursor:
        request = f"SELECT * FROM {group_name} WHERE status = 'owner'"
        cursor.execute(request)
        result = cursor.fetchall()
        return result


def update_date(group_name, id):
    connection = table_connect()
    with connection.cursor() as cursor:
        request = f"UPDATE {group_name} SET last_join_time = '{get_current_time()}' WHERE id = {id};"
        cursor.execute(request)
        connection.commit()
    return "200"


def get_tables():
    connection = table_connect()
    with connection.cursor() as cursor:
        request = "show tables"
        cursor.execute(request)
        result = cursor.fetchall()
    return result


def find_user_in_group(group_name, id):
    connection = table_connect()
    with connection.cursor() as cursor:
        request = f"select * from {group_name} where id = {id}"
        cursor.execute(request)
        result = cursor.fetchall()
    return result




def find_group_with_id(id):
    tables = []
    for table in get_tables():
        tables.append(table["Tables_in_buh"])
    for table in tables[1:]:
        if find_user_in_group(table, id) != ():
            return table
    return False


def get_time_of_group_members(group_name):
    connection = table_connect()
    with connection.cursor() as cursor:
        request = f"select * from {group_name} order by student_name;"
        cursor.execute(request)
        result = cursor.fetchall()
    return result
