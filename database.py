import pymysql
from creds import password, user

def connect_totable(db_name):
    connections = pymysql.connect(
        host="localhost",
        port=3306,
        user=user,
        db=db_name,
        password=password,
        cursorclass=pymysql.cursors.DictCursor)
    print("подключение к бд прошло успешно...")
    return connections


def create_group(group_name, group_id, admin_id):
    connections = connect_totable("BUH")
    with connections.cursor() as cursor:
        sql = f"CREATE table IF NOT EXISTS {group_name} (id INT PRIMARY KEY, student_name VARCHAR(50));"
        cursor.execute(sql)
        connections.commit()
    connections = connect_totable("BUH")
    with connections.cursor() as cursor:
        sql = f"INSERT INTO groups_ids (group_id, group_name, admin_id) values (%s, %s, %s)"
        cursor.execute(sql, (group_id, group_name, admin_id))
        connections.commit()
    return


def add_user(id, student_name, group):
    connections = connect_totable("BUH")
    with connections.cursor() as cursor:
        sql = f"INSERT INTO {group} (id, sudent_name) values (%s, %s);"
        cursor.execute(sql, (id, student_name))
        connections.commit()
