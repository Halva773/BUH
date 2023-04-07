import pymysql.cursors

from creds import password, user



def table_connect():
    connections = pymysql.connect(
        host="localhost",
        port=3306,
        user=user,
        db="BUH",
        password=password,
        cursorclass=pymysql.cursors.DictCursor)
    print(f"[INFO] Подключение к бд прошло успешно...")
    return connections


def create_group(group_name, group_id, admin_id, admin_name):
    connection = table_connect()
    with connection.cursor() as cursor:
        sql = f"CREATE table IF NOT EXISTS {group_name} (id BIGINT UNSIGNED PRIMARY KEY, student_name VARCHAR(50), status VARCHAR(10));"
        cursor.execute(sql)
        sql = f"INSERT INTO {group_name} (id, student_name, status) values (%s, %s, %s)"
        cursor.execute(sql, (admin_id, admin_name, "owner"))
        sql = f"INSERT INTO groups_ids (group_id, group_name) values (%s, %s)"
        cursor.execute(sql, (group_id, group_name))
        connection.commit()
    return


def join_user(id, student_name, group, status):
    connections = table_connect()
    with connections.cursor() as cursor:
        sql = f"INSERT INTO {group} (id, student_name, status) values (%s, %s, %s);"
        cursor.execute(sql, (id, student_name, status))
        connections.commit()


def response_handler(action, group_name, user_id):
    connections = table_connect()
    with connections.cursor() as cursor:
        if action:
            sql = f"update {group_name} set status = 'member' where id = {user_id}"
        else:
            sql = f"delete {group_name} where id = {user_id}"
        cursor.execute(sql)
        connections.commit()

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
