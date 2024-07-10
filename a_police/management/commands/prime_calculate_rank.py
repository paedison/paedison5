import traceback

import django.db.utils
from django.core.management.base import BaseCommand
from django.db import transaction

from a_police.models import PrimeStudent


def get_score_and_participants(student: PrimeStudent, queryset: PrimeStudent) -> tuple[dict, dict]:
    score = {}
    participants = {}
    rank = {}
    for field, value in student.score.items():
        score[field] = []
        for qs in queryset:
            if field in qs['score'].keys():
                score[field].append(qs['score'][field])
        participants[field] = len(score[field])
        if field in student.score.keys():
            sorted_score = sorted(score[field], reverse=True)
            rank[field] = sorted_score.index(student.score[field]) + 1
    return rank, participants


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
            qs_all_score_total = qs_student.values('score')

            rank_total, participants_total = get_score_and_participants(
                student=student, queryset=qs_all_score_total)

            if student.rank_total != rank_total or student.participants_total != participants_total:
                student.rank_total = rank_total
                student.participants_total = participants_total
                update_list.append(student)
                update_count += 1

        try:
            with transaction.atomic():
                if update_list:
                    PrimeStudent.objects.bulk_update(update_list, ['rank_total', 'participants_total'])
                    message = f'Successfully {update_count} PrimeStudent instances updated.'
                else:
                    message = f'PrimeStudent instances already exist.'
        except django.db.utils.IntegrityError:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            message = f'Error occurred.'

        self.stdout.write(self.style.SUCCESS(message))
