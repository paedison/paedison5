import traceback
from collections import Counter

import django.db.utils
from django.core.management.base import BaseCommand
from django.db import transaction

from a_police.models import PrimeStudent, PrimeAnswerCount


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
        create_list = []
        create_count = 0

        field_dict = {
            'hyeongsa': '형사',
            'heonbeob': '헌법',
            'gyeongchal': '경찰',
            'beomjoe': '범죄',
            'haengbeob': '행법',
            'haenghag': '행학',
            'minbeob': '민법',
            'sebeob': '세법',
            'hoegye': '회계',
            'sangbeob': '상법',
            'gyeongje': '경제',
            'tonggye': '통계',
            'jaejeong': '재정',
            'jeongbo': '정보',
            'sine': '시네',
            'debe': '데베',
            'tongsin': '통신',
            'sowe': '소웨'
        }

        total_count = {}
        for field, subject in field_dict.items():
            total_count[field] = []
            for i in range(1, 41):
                total_count[field].append(
                    {
                        'year': exam_year, 'exam': '', 'round': exam_round,
                        'subject': subject, 'number': i, 'answer': 0,
                        'count_1': 0, 'count_2': 0, 'count_3': 0, 'count_4': 0, 'count_5': 0,
                        'count_0': 0, 'count_None': 0, 'count_multiple': 0, 'count_total': 0,
                    },
                )

        qs_student = PrimeStudent.objects.filter(year=exam_year, round=exam_round)

        total_answer_lists = {field: [] for field in field_dict}
        for student in qs_student:
            for field, answer in student.answer.items():
                total_answer_lists[field].append(answer)

        for field, answer_lists in total_answer_lists.items():
            if answer_lists:
                distributions = [Counter() for _ in range(40)]
                for lst in answer_lists:
                    for i, value in enumerate(lst):
                        if value > 5:
                            distributions[i]['count_multiple'] += 1
                        else:
                            distributions[i][value] += 1

                for index, counter in enumerate(distributions):
                    count_1 = counter.get(1, 0)
                    count_2 = counter.get(2, 0)
                    count_3 = counter.get(3, 0)
                    count_4 = counter.get(4, 0)
                    count_5 = counter.get(5, 0)
                    count_0 = counter.get(0, 0)
                    count_multiple = counter.get('count_multiple', 0)
                    count_total = sum([count_1, count_2, count_3, count_4, count_5, count_0, count_multiple])
                    total_count[field][index].update({
                        'count_1': count_1,
                        'count_2': count_2,
                        'count_3': count_3,
                        'count_4': count_4,
                        'count_5': count_5,
                        'count_multiple': count_multiple,
                        'count_total': count_total,
                    })

        field_list_for_matching = [
            'count_1', 'count_2', 'count_3', 'count_4', 'count_5',
            'count_0', 'count_None', 'count_multiple', 'count_total',
        ]

        for field in field_dict.keys():
            for c in total_count[field]:
                if c['count_total']:
                    try:
                        obj = PrimeAnswerCount.objects.get(
                            year=exam_year, round=exam_round,
                            subject=c['subject'],
                            number=c['number'],
                        )
                        fields_not_match = any(getattr(obj, field) != c[field] for field in field_list_for_matching)
                        if fields_not_match:
                            for fld in field_list_for_matching:
                                setattr(obj, fld, c[fld])
                            update_list.append(obj)
                            update_count += 1
                    except PrimeAnswerCount.DoesNotExist:
                        create_list.append(PrimeAnswerCount(**c))
                        create_count += 1

        try:
            with transaction.atomic():
                if create_list:
                    PrimeAnswerCount.objects.bulk_create(create_list)
                    message = f'Successfully created {create_count} PrimeAnswerCount instances.'
                if update_list:
                    PrimeAnswerCount.objects.bulk_update(update_list, field_list_for_matching)
                    message = f'Successfully updated {update_count} PrimeAnswerCount instances.'
                if not create_list and not update_list:
                    message = f'No changes were made to PrimeAnswerCount instances.'
        except django.db.utils.IntegrityError:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            message = 'An error occurred during the transaction.'

        self.stdout.write(self.style.SUCCESS(message))
