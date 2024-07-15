from flask import url_for
from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


def check_password(password, project_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT * FROM projects WHERE id = %s AND password = %s;',
                (project_id, password, )
            )
            data = cursor.fetchone()
    return bool(data)


def get_admin_name(project_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT u.full_name FROM projects p INNER JOIN users u ON p.admin_id = u.id WHERE p.id = %s;',
                (project_id, )
            )
            data = cursor.fetchone()
    return data['full_name']


def check_user(user_id, project_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                '''SELECT admin_id FROM projects WHERE id = %s AND admin_id = %s
                   UNION
                   SELECT user_id FROM project_workers WHERE user_id = %s AND project_id = %s;''',
                (project_id, user_id, user_id, project_id, )
            )
            data = cursor.fetchone()            
    return bool(data)


def get_last_project_id():
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT id FROM projects LIMIT 1;')
            data = cursor.fetchone()
    if data is None:
        return 0
    return data['id']


def create_new_project(name, password, admin_id, db_name):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO projects(`name`, `password`, `admin_id`, `db_name`) VALUES (%s, %s, %s, %s);',
                (name, password, admin_id, db_name, )
            )
        connection.commit()


def create_project_database(db_name):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE {db_name};')
        connection.commit()
    
    with open('help/project_db.sql', 'r', encoding='utf-8') as f:
        query = f.read() 
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=db_name) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()


def check_project_admin(project_id, user_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT admin_id FROM projects WHERE id = %s;',
                (project_id, )
            )
            data = cursor.fetchone()            
    return data['admin_id'] == user_id


def get_project_db_data(project_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT db_host, db_user, db_pass, db_name FROM projects WHERE id = %s;',
                (project_id, )
            )
            data = cursor.fetchone()            
    return data['db_host'], data['db_user'], data['db_pass'], data['db_name']


def insert_faculty_db(name, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO faculties(`name`) VALUES (%s);',
                (name, )
            )
        connection.commit()


def insert_department_db(name, faculty, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO departments(`name`, `faculty`) VALUES (%s, %s);',
                (name, int(faculty), )
            )
        connection.commit()


def insert_spec_db(spec_name, spec_department, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO specialities(`name`, `department`) VALUES (%s, %s);',
                (spec_name, int(spec_department), )
            )
        connection.commit()


def insert_group_db(group_name, group_students, group_spec, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO `groups`(`name`, `students_count`, `speciality`) VALUES (%s, %s, %s);',
                (group_name, group_students, int(group_spec), )
            )
        connection.commit()


def insert_teacher_db(teacher_name, teacher_department, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO teachers(`name`, `department`) VALUES (%s, %s);',
                (teacher_name, int(teacher_department), )
            )
        connection.commit()


def insert_aud_db(aud_name, aud_size, aud_faculty, aud_department, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO classrooms(`number`, `size`, `faculty`, `department`) VALUES (%s, %s, %s, %s);',
                (aud_name, aud_size, int(aud_faculty), int(aud_department) if aud_department else None, )
            )
        connection.commit()


def insert_subject_db(subject_name, short_name, subject_group, subject_department, hours, main_techer, second_techer, project_id):
    host, user, password, db = get_project_db_data(project_id)
    print(hours)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO subjects(`name`, `short_name`, `group`, `department`, `hours`, `main_teacher`, `second_teacher`)' \
                ' VALUES (%s, %s, %s, %s, %s, %s, %s);',
                (subject_name, short_name, int(subject_group), int(subject_department), hours, int(main_techer), 
                int(second_techer) if second_techer else None, )
            )
        connection.commit()


def insert_worker_db(worker_id, project_id):
    with connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO project_workers(`user_id`, `project_id`) VALUES (%s, %s);',
                (worker_id, project_id, )
            )
        connection.commit()


def get_project_faculties(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT id, name FROM faculties ')
            data = cursor.fetchall()            
    return data


def get_project_departments(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT d.id, d.name, f.name as faculty_name FROM departments d inner join faculties f on d.faculty = f.id order by f.id;'
            )
            data = cursor.fetchall()
    return data


def get_project_specs(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT s.id, s.name, d.name as department_name FROM specialities s inner join departments d on s.department = d.id;'
            )
            data = cursor.fetchall()
    return data


def get_project_groups(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT g.id, g.name, s.name as spec_name, d.name as department_name, f.id as faculty_id
                FROM `groups` g 
                inner join specialities s on g.speciality = s.id 
                inner join departments d on s.department = d.id
                inner join faculties f on d.faculty = f.id
                order by d.id;
            ''')
            data = cursor.fetchall()
    return data


def get_project_teachers(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT t.id, t.name, d.name as department_name FROM teachers t inner join departments d on t.department = d.id;')
            data = cursor.fetchall()
    return data


def get_project_classrooms(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT c.id, c.number as `name`, f.name as faculty_name, d.name as department_name 
                FROM classrooms c 
                inner join faculties f on c.faculty = f.id
                left join departments d on c.department = d.id;
            ''')
            data = cursor.fetchall()
    for i in range(len(data)):
        if data[i]['department_name'] is None:
            data[i]['department_name'] = ''
    return data


def get_project_subjects(project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT s.id, s.name, s.short_name, s.hours, g.name as `group`, d.name as `department`, 
                    t1.name as `main_teacher`, t2.name as `second_teacher`, g.id as `group_id`
                FROM subjects s 
                inner join `groups` g on s.group = g.id
                inner join departments d on s.department = d.id
                inner join teachers t1 on s.main_teacher = t1.id
                left join teachers t2 on s.second_teacher = t2.id;
            ''')
            data = cursor.fetchall()
    for i in range(len(data)):
        if data[i]['second_teacher'] is None:
            data[i]['second_teacher'] = ''
    return data


def get_schedule(project_id, groups):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    pairs = [
        '1 пара [08:00 - 09:35]',
        '2 пара [09:50 - 11:25]',
        '3 пара [11:40 - 13:15]',
        '4 пара [13:45 - 15:20]',
        '5 пара [15:35 - 17:10]',
        '6 пара [17:25 - 19:00]',
        '7 пара [19:15 - 20:50]',
        '8 пара [21:05 - 22:35]'
    ]
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT s.id, s.week, s.day_number, s.pair_number, g.name as `group`, c.number as `classroom`, 
                       sb.short_name as `subject`, t1.name as `main_teacher`, t2.name as `second_teacher` 
                FROM schedule s 
                inner join `groups` g on s.`group` = g.id 
                inner join classrooms c on s.classroom = c.id
                inner join subjects sb on s.subject = sb.id
                inner join teachers t1 on sb.main_teacher = t1.id
                left join teachers t2 on sb.second_teacher = t2.id;
            ''')
            data = cursor.fetchall()
    result = {group['name']: [[[{'id': None, 'pair_number': pair_num} for pair_num in range(1, 9)] for _ in range(6)] for _ in range(2)] for group in groups}
    for i in data:
        i['main_teacher'] = i['main_teacher'].split(' ')
        i['main_teacher'] = i['main_teacher'][0] + ' ' + '. '.join(l[0] for l in i['main_teacher'][1:])
        if i['second_teacher']:
            i['second_teacher'] = i['second_teacher'].split(' ')
            i['second_teacher'] = i['second_teacher'][0] + ' ' + '. '.join(j[0] for j in i['second_teacher'][1:] if j)
        teacher_string = i['main_teacher'] if not i['second_teacher'] else f'{i["main_teacher"]},</p><p class="text-center">{i["second_teacher"]}'
        i['teacher_string'] = teacher_string
        result[i['group']][i['week']][i['day_number']][i['pair_number']] = i
    return result


def insert_cell_db(group_id, week, day_number, pair_number, subject, classroom, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO schedule(`group`, `week`, `day_number`, `pair_number`, `subject`, `classroom`) VALUES (%s, %s, %s, %s, %s, %s);',
                (group_id, week, day_number, pair_number, subject, classroom, )
            )
        connection.commit()


def del_cell_db(cell_id, project_id):
    host, user, password, db = get_project_db_data(project_id)
    with connect(host=host, user=user, password=password, database=db) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'DELETE FROM schedule WHERE id=%s;',
                (cell_id, )
            )
        connection.commit()