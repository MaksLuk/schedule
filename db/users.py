from mysql.connector import connect
from config import *


def get_user_type(user_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT t.name FROM users u INNER JOIN user_types t ON u.user_type = t.id WHERE u.id = %s;',
                (user_id, )
            )
            data = cursor.fetchone()
    return data['name']


def show_user_projects(user_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                '''SELECT p.id, p.name, u.full_name as admin_name 
                   FROM projects p 
                   INNER JOIN users u ON p.admin_id = u.id 
                   WHERE p.admin_id = %s
                   UNION
                   SELECT p.id, p.name, u.full_name as admin_name  
                   FROM project_workers w
                   INNER JOIN projects p ON w.project_id = p.id
                   INNER JOIN users u ON w.user_id = u.id 
                   WHERE w.user_id = %s;''',
                (user_id, user_id, )
            )
            data = cursor.fetchall()
    return data