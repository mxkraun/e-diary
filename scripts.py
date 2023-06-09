from datacenter.models import *
import random
from datetime import datetime


COMMENDATION_PHRASES = (
        'Очень хороший ответ!', 'Талантливо!', 'Уже существенно лучше!',
        'Ты на верном пути!', 'С каждым разом у тебя получается всё лучше!',
        'Я вижу, как ты стараешься!', 'Ты растешь над собой!'
        )


class EmptyQuerySet(Exception):
    def __str__(self):
        return f'QuerySet is empty.'


def fix_marks(schoolkid):
    Mark.objects.filter(schoolkid=schoolkid, points__in=[2,3]).update(points=5)


def remove_chastisements(schoolkid):
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    chastisements.delete()


def create_commendation(schoolkid, subject_title): 
    group_letter = schoolkid.group_letter
    year_of_study = schoolkid.year_of_study
    while True:
        try:
            date_input = input('Введите дату урока в формате Y-m-d: ')
            lesson_date = datetime.strptime(date_input, '%Y-%m-%d')
            break
        except:
            print('Неверный формат даты. Попробуйте еще раз. Пример: 2019-01-01.')
    lessons = Lesson.objects.filter(
        group_letter=group_letter, year_of_study=year_of_study,
        subject__title=subject_title, date=lesson_date
        ).order_by('date')
    lessons_count = lessons.count()
    if lessons_count > 1:
        print(f'Все уроки {date_input} по предмету {subject_title}:')
        for i, lesson in enumerate(lessons, 1):
            lesson_time = lesson.TIMESLOTS_SCHEDULE[lesson.timeslot - 1]
            print(f'Урок № {i}. Учитель: {lesson.teacher}, Время: {lesson_time}, Класс: {lesson.room}')
        while True:
            try: 
                lesson_number_input =  input('Введите номер нужного урока: ')
                lesson = lessons[int(lesson_number_input) - 1]
                break
            except:
                print('Неверный номер урока. Попробуйте еще раз.')
    elif lessons_count == 1:
        lesson = lessons[0]
    else: 
        raise EmptyQuerySet
    Commendation.objects.create(
        text=random.choice(COMMENDATION_PHRASES), created=lesson.date,schoolkid=schoolkid,
        subject=lesson.subject, teacher=lesson.teacher
        )


def main():
    while True:
        try:
            schoolkid_name = input('Введите ФИО ученика: ')
            schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
            print('Ученик найден.')
            break
        except Schoolkid.MultipleObjectsReturned:
            print('Найдено несколько таких учеников. Уточните ФИО.')
        except Schoolkid.DoesNotExist:
            print('Такой ученик не найден. Попробуйте еще раз.')

    print('Исправляем оценки...')
    fix_marks(schoolkid)
    print('Оценки исправлены.')

    print('Удаляем замечания...')
    remove_chastisements(schoolkid)
    print('Замечания удалены.')

    while True:
        try:
            subject_title = input('Введите название предмета для создания похвалы(с большой буквы): ')
            create_commendation(schoolkid, subject_title)
            print('Похвала создана.')
            break
        except EmptyQuerySet:
            print('Не найдено нужных уроков. Попробуйте еще раз.')

    print('Все готово!')


if __name__ == '__main__':
    main()
    