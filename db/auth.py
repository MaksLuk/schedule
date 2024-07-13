from mysql.connector import connect
from config import *


def get_strategy_types():
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT id, `name` FROM strategy_types;')
            data = cursor.fetchall()
    return data


def create_user(email, name, password):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('INSERT INTO users(`email_address`, `full_name`, `password`) VALUES (%s, %s, %s);',
                           (email, name, password))
        connection.commit()


def show_user_with_email(email):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM users WHERE `email_address`=%s;', (email, ))
            data = cursor.fetchone()
    return data


def show_user(email, password):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM users WHERE `email_address`=%s AND `password`=%s;', (email, password))
            data = cursor.fetchone()
    return data


def get_user_types():
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM user_types;')
            data = cursor.fetchall()
    result = dict()
    for i in data:
        result[i['name']] = i['id']
    return result

