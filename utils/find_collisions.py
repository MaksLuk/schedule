from db.projects import (
    get_project_groups, get_project_classrooms, get_project_subjects, get_schedule, 
)

def find_collisions(project_id):
    # получение данных из бд
    groups = get_project_groups(project_id)
    classrooms = get_project_classrooms(project_id)
    subjects = get_project_subjects(project_id)
    schedule = get_schedule(project_id, groups)

    # получение коллизий
    subject_collisions = find_subjects_hours_collisions(subjects, schedule)
    classroom_collisions = find_classrooms_collisions(schedule, classrooms, groups)
    teacher_collisions = find_teacher_collisions(schedule)
    return subject_collisions, classroom_collisions, teacher_collisions


def find_teacher_collisions(schedule):
    ''' ищет случаи, когда учитель в одно и то же время проводит более 2 пар '''
    errors = []
    teachers = dict()
    for group in schedule:
        for week_index, week in enumerate(schedule[group]):
            for day_index, day in enumerate(week):
                for pair_index, pair in enumerate(day):
                    if not pair['id']:
                        continue
                    for current_teacher in [pair['main_teacher'], pair['second_teacher']]:
                        if not current_teacher in teachers:
                            teachers[current_teacher] = {
                                week: {day: {pair_num: False for pair_num in range(8)} for day in range(6)} for week in range(2)
                            }
                        if teachers[current_teacher][week_index][day_index][pair_index]:
                            errors.append([current_teacher, pair])
    return errors


def find_classrooms_collisions(schedule, all_classrooms, groups):
    ''' находит 2 вида ошибок:
        1) аудитория занята в этот момент времени
        2) аудитория слишком мала для группы
    '''
    errors = []
    size_errors = []
    classrooms = {
        classroom['name']: {
            week: {
                day: {
                    pair: False for pair in range(8)
                } for day in range(6)
            } for week in range(2)
        } for classroom in all_classrooms
    }
    classroom_size = {i['name']: i['size'] for i in all_classrooms}
    group_size = {i['name']: i['students_count'] for i in groups}
    for group in schedule:
        for week_index, week in enumerate(schedule[group]):
            for day_index, day in enumerate(week):
                for pair_index, pair in enumerate(day):
                    if not pair['id']:
                        continue
                    if group_size[pair['group']] > classroom_size[pair['classroom']]:
                        size_errors.append(pair)
                    if classrooms[pair['classroom']][week_index][day_index][pair_index]:
                        errors.append(pair)
                    else:
                        classrooms[pair['classroom']][week_index][day_index][pair_index] = True                    
    return errors, size_errors


def find_subjects_hours_collisions(subjects, schedule):
    ''' возвращает три переменные: 
        массив предметов, по которым указаны лишние пары,
        массив предметов, по которым слишком большая разница в числе пар между неделями (0 либо 3 пары на одной неделе),
        массив предметов, по которым указаны не все пары
    '''
    subject_in_2_week, subjects_count_in_weeks, errors = get_subjects_hours(subjects, schedule)
    week_defference = []
    for i in subjects_count_in_weeks:       # смотрим на число пар одного предмета в 1 и 2 неделях
        if i in subject_in_2_week:          # смотрим только на предметы, расписание по которым полностью составлено
            continue
        if i in errors:                     # не смотрим на ошибки
            continue
        if 0 in subjects_count_in_weeks[i] or 3 in subjects_count_in_weeks[i]:
            week_defference.append(i)
    return errors, week_defference, list(subject_in_2_week.keys())


def get_subjects_hours(subjects, schedule):
    hours = {72: 2, 108: 3, 144: 4}
    subject_in_2_week = dict()
    subjects_count_in_weeks = {i['name'] + ' ' + i['group']: [0, 0] for i in subjects}
    errors = []
    for subject in subjects:
        subject['name'] = subject['name'] + ' ' + subject['group']
        current_subject_count = 0
        for week_number, week in enumerate(schedule[subject['group']]):
            for day in week:
                for pair in day:
                    if pair['id'] != None and pair['subject'] == subject['short_name']:
                        current_subject_count += 1
                        subjects_count_in_weeks[subject['name']][week_number] += 1
        if hours[subject['hours']] - current_subject_count < 0:
            errors.append(subject['name'])
        if hours[subject['hours']] - current_subject_count > 0:
            subject_in_2_week[subject['name']] = hours[subject['hours']] - current_subject_count
    return subject_in_2_week, subjects_count_in_weeks, errors