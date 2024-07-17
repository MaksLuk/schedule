from db.projects import (
    get_project_groups, get_project_classrooms, get_project_subjects, get_schedule, insert_cell_db
)
from utils.find_collisions import get_subjects_hours


def create_simple_schedule(project_id):
    # получение исходных данных
    groups = get_project_groups(project_id)
    classrooms = get_project_classrooms(project_id)
    subjects = get_project_subjects(project_id)
    schedule = get_schedule(project_id, groups)

    # доп. данные
    groups_id = {i['name']: i['id'] for i in groups}
    group_counts = {i['name']: i['students_count'] for i in groups}
    subjects_ids = {i['name'] + ' ' + i['group']: i['id'] for i in subjects}

    # поиск недостающих предметов
    subject_in_2_week, subjects_count_in_weeks, errors = get_subjects_hours(subjects, schedule)
    if errors:
        return errors

    # вставка расписания ПЕРЕСМОТРЕТЬ
    for subject in subject_in_2_week:
        group = subject.split(' ')[-1]
        for _ in range(subject_in_2_week[subject]):
            avg_pair_number = get_avg_group_pair_number(schedule, group) 
            min_week, min_day = get_day_with_min_pairs(schedule, group)
            current_pair = 99
            for pair_number, pair in enumerate(schedule[group][min_week][min_day]):
                if pair['id'] == None:
                    if abs(avg_pair_number - pair_number) < abs(avg_pair_number - current_pair):
                        current_pair = pair_number
            classroom = find_classroom(schedule, classrooms, min_week, min_day, current_pair, group_counts[group])
            insert_cell_db(groups_id[group], min_week, min_day, current_pair, subjects_ids[subject], classroom, project_id)
            schedule = get_schedule(project_id, groups)


def find_classroom(schedule, classrooms, week, day, pair, min_count):
    free_classrooms = []
    for classroom in classrooms:
        if classroom['size'] < min_count:
            continue
        for i in schedule:
            if not schedule[i][week][day][pair]['id']:
                continue
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
    for week_number, week in enumerate(schedule[group]):
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