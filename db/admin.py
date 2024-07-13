from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


def show_users():
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                '''SELECT u.id, u.full_name as `name`, t.full_name as status 
                   FROM users u
                   INNER JOIN user_types t ON u.user_type = t.id
                   WHERE t.name != 'admin';'''
            )
            data = cursor.fetchall()
    return data


def show_projects():
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                '''SELECT p.id, p.name, p.password, u.full_name as 'admin_name'
                   FROM projects p 
                   INNER JOIN users u ON p.admin_id = u.id;'''
            )
            data = cursor.fetchall()
    return data


def show_admin(user_id, password):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT id FROM user_types WHERE `name`="Администратор";')
            data = cursor.fetchone()
            cursor.execute('SELECT * FROM users WHERE id = %s AND password = %s AND user_type = %s;',
                           (user_id, password, data['id']))
            data = cursor.fetchone()
    return data