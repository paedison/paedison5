import traceback

import django.db.utils
from django.core.management.base import BaseCommand
from django.db import transaction

from a_police.models import PrimeStudent, Exam


class Command(BaseCommand):
    help = 'Count Answers'

    def add_arguments(self, parser):
        parser.add_argument('year', type=str, help='Year')
        parser.add_argument('round', type=str, help='Round')

    def handle(self, *args, **kwargs):
        exam_year = kwargs['year']
        exam_round = kwargs['round']

        update_list = []
        update_count = 0

        qs_student = PrimeStudent.objects.filter(year=exam_year, round=exam_round)
        for student in qs_student:
            answer_official = Exam.objects.get(
                year=student.year, exam=student.exam, round=student.round).answer_official
            answer_student: dict = student.answer
            score = {}
            for field, value in answer_student.items():
                if field in ['hyeongsa', 'gyeongchal']:
                    score_per_problem = 3
                elif field in ['sebeob','hoegye', 'jeongbo', 'sine']:
                    score_per_problem = 2
                elif field in ['haengbeob', 'haenghag', 'minbeob']:
                    score_per_problem = 1
                else:
                    score_per_problem = 1.5

                correct_count = 0
                for index, answer in enumerate(value):
                    if answer == answer_official[field][index]:
                        correct_count += 1
                score[field] = correct_count * score_per_problem
            score['sum'] = sum(s for s in score.values())
            score['avg'] = score['sum'] / 5

            if student.score != score:
                student.score = score
                update_list.append(student)
                update_count += 1

        try:
            with transaction.atomic():
                if update_list:
                    PrimeStudent.objects.bulk_update(update_list, ['score'])
                    message = f'Successfully {update_count} PrimeStudent instances updated.'
                else:
                    message = f'PrimeStudent instances already exist.'
        except django.db.utils.IntegrityError:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            message = f'Error occurred.'

        self.stdout.write(self.style.SUCCESS(message))
