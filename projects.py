from flask import Blueprint
from flask import render_template, request, redirect, url_for, session, jsonify

from db.projects import (
    check_password, check_user, get_last_project_id, create_new_project, 
    check_project_admin, insert_faculty_db, insert_department_db,
    insert_spec_db, insert_group_db, insert_teacher_db, insert_aud_db,
    insert_subject_db, insert_worker_db, get_project_faculties, get_admin_name,
    create_project_database, get_project_departments, get_project_specs,
    get_project_groups, get_project_teachers, get_project_classrooms,
    get_project_subjects, get_schedule, insert_cell_db, del_cell_db, 
)
from db.users import get_user_type
from db.admin import show_users


projects = Blueprint('projects', __name__, template_folder='templates', static_folder='static')


def render_template_project(project_id, user_id):
    faculties = get_project_faculties(project_id)
    for i in range(len(faculties)):
        faculties[i]['index'] = i
    departments = get_project_departments(project_id)
    specs = get_project_specs(project_id)
    groups = get_project_groups(project_id)
    teachers = get_project_teachers(project_id)
    classrooms = get_project_classrooms(project_id)
    subjects = get_project_subjects(project_id)
    admin_name = get_admin_name(project_id)
    workers = [i for i in show_users() if i['id'] != user_id]

    schedule = get_schedule(project_id, groups)
    return render_template(
        'project.html', project_id=project_id, faculties=faculties, departments=departments, 
        specs=specs, groups=groups, teachers=teachers, auds=classrooms, subjects=subjects, schedule=schedule,
        admin_name=admin_name, workers=workers, enumerate=enumerate
    )


def create_simple_schedule(project_id):
    # получение исходных данных
    groups = get_project_groups(project_id)
    classrooms = get_project_classrooms(project_id)
    subjects = get_project_subjects(project_id)
    schedule = get_schedule(project_id, groups)

    # доп. данные
    groups_id = {i['name']: i['id'] for i in groups}
    group_counts = {i['name']: i['students_count'] for i in groups}

    # поиск недостающих предметов
    hours = {72: 2, 108: 3, 144: 4}
    subject_in_2_week = dict()
    subjects_count_in_weeks = {i['name']: [0, 0] for i in subjects}
    for subject in subjects:
        current_subject_count = 0
        for week_number, week in enumerate(schedule[subject['group']]):
            for day in week:
                for pair in day:
                    if pair['id'] != None and pair['subject'] == subject['short_name']:
                        current_subject_count += 1
                        subjects_count_in_weeks[subject['name']][week_number] += 1
        if hours[subject['name']] - current_subject_count < 0:
            return subject['name'] + ' ' + subject['group']
        if hours[subject['name']] - current_subject_count > 0:
            subject_in_2_week[subject['name']] = hours[subject['name']] - current_subject_count

    # вставка расписания
    for subject in subject_in_2_week:
        for _ in range(subject_in_2_week[subject]):
            avg_pair_number = get_avg_group_pair_number(schedule, subject['group']) 
            min_week, min_day = get_day_with_min_pairs(schedule, subject['group'])
            current_pair = 99
            for pair_number, pair in enumerate(schedule[subject['group']][min_week][min_day]):
                if pair['id'] == None:
                    if abs(avg_pair_number - pair_number) < abs(avg_pair_number - current_pair):
                        current_pair = pair_number
            classroom = find_classroom(schedule, classrooms, min_week, min_day, current_pair, group_counts[subject['group']])
            insert_cell_db(groups_id[subject['group']], min_week, min_day, current_pair, subject['id'], classroom, project_id)
            schedule = get_schedule(project_id, groups)


def find_classroom(schedule, classrooms, week, day, pair, min_count):
    free_classrooms = []
    for classroom in classrooms:
        if classroom['size'] < min_count:
            continue
        for i in schedule:
            if schedule[i][week][day][pair]['classroom'] == classroom['name']:
                continue
        return classroom['id']


def get_avg_group_pair_number(schedule, group):
    all_pair_numbers = []
    for week in schedule[group]:
        for day in week:
            for pair in day:
                if pair['id'] != None and pair['group'] == group:
                    all_pair_numbers.append(pair['pair_number'])
    if not all_pair_numbers:
        return 3
    return int( sum(all_pair_numbers) / len(all_pair_numbers) )


def get_day_with_min_pairs(schedule, group):
    min_week = 0
    min_day = 0
    min_pairs = 99
    for week_number, week in enumerate(schedule[subject['group']]):
        for day_number, day in enumerate(week):
            pairs_in_day = 0
            for pair in day:
                if pair['id'] != None and pair['group'] == group:
                    pairs_in_day += 1
            if pairs_in_day < min_pairs:
                min_week = week_number
                min_day = day_number
                min_pairs = pairs_in_day
    return min_week, min_day


@projects.route('/project', methods=['GET', 'POST'])
def project():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        project_id = request.args.get('id')
        return render_template('project_password.html', id=project_id)

    password = request.form['password']
    project_id = int(request.form['id'])
    if not check_password(password, project_id):
        return jsonify({'error': 'Неверный пароль'}), 403
    if not check_user(session['id'], project_id):
        return jsonify({'error': 'У вас нет доступа к этому проекту'}), 403

    return render_template_project(project_id, session['id'])


@projects.route('/insert_project', methods=['POST'])
def insert_project():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    user_type = get_user_type(session['id'])
    if user_type != 'admin':
        return jsonify({'error': 'Вы не можете создавать проекты'}), 403
    
    project_name = request.form['project_name']
    project_pass = request.form['project_pass']
    project_admin = request.form['project_admin']
    next_project_id = get_last_project_id() + 1
    project_db_name = f'project_db_{next_project_id}'

    create_new_project(project_name, project_pass, project_admin, project_db_name)
    create_project_database(project_db_name)
    return redirect(url_for('index'))


@projects.route('/insert_faculty', methods=['POST'])
def insert_faculty():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    faculty_name = request.form['faculty_name']
    insert_faculty_db(faculty_name, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/insert_department', methods=['POST'])
def insert_department():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    department_name = request.form['department_name']
    department_faculty = request.form['department_faculty']
    insert_department_db(department_name, department_faculty, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/insert_spec', methods=['POST'])
def insert_spec():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    spec_name = request.form['spec_name']
    spec_department = request.form['spec_department']
    insert_spec_db(spec_name, spec_department, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/insert_group', methods=['POST'])
def insert_group():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    group_name = request.form['group_name']
    group_students = int(request.form['group_students'])
    group_spec = request.form['group_spec']
    insert_group_db(group_name, group_students, group_spec, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/insert_teacher', methods=['POST'])
def insert_teacher():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    teacher_name = request.form['teacher_name']
    teacher_department = request.form['teacher_department']
    insert_teacher_db(teacher_name, teacher_department, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/insert_aud', methods=['POST'])
def insert_aud():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    aud_name = request.form['aud_name']
    aud_size = int(request.form['aud_size'])
    aud_faculty = request.form['aud_faculty']
    aud_department = request.form['aud_department']
    if aud_department == '-':
        aud_department = None
    insert_aud_db(aud_name, aud_size, aud_faculty, aud_department, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/insert_subject', methods=['POST'])
def insert_subject():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    subject_name = request.form['subject_name']
    short_name = request.form['short_name']
    subject_group = request.form['subject_group']
    subject_department = request.form['subject_department']
    hours = int(request.form['subject_hours'])
    main_techer = request.form['subject_main_techer']
    second_techer = request.form['subject_second_techer']
    if second_techer == '-':
        second_techer = None
    insert_subject_db(subject_name, short_name, subject_group, subject_department, hours, main_techer, second_techer, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/add_worker', methods=['POST'])
def add_worker():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    if not check_project_admin(project_id, session['id']):
        return jsonify({'error': 'Вы не имеете прав для редактирования входных данных проекта'}), 403
    
    worker_id = request.form['add_worker_id']
    insert_worker_db(worker_id, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/add_cell', methods=['POST'])
def add_cell():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    group_id = request.form['group_id']
    week = int(request.form['week']) - 1
    day_number = int(request.form['day_number'])
    pair_number = int(request.form['pair_number'])
    subject = request.form['cell_subject_name']
    classroom = request.form['cell_classroom_name']
    insert_cell_db(group_id, week, day_number, pair_number, subject, classroom, project_id)
    return render_template_project(project_id, session['id'])


@projects.route('/del_cell', methods=['POST'])
def del_cell():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    project_id = request.form['project_id']
    cell_id = request.form['cell_id']
    del_cell_db(cell_id, project_id)
    return render_template_project(project_id, session['id'])