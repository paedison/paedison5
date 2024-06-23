import os

import pandas as pd
from django.conf import settings
from django.db import transaction
from django.db.models import Count, QuerySet
from django.urls import reverse_lazy
from pandas import DataFrame

from a_common.constants import icon_set
from a_common.utils import detect_encoding, HtmxHttpRequest
from a_predict.models import (
    Exam, Unit, Department, Location,
    Student, StudentAnswer, SubmittedAnswer, AnswerCount, OfficialAnswer,
)


class ExamInfo:
    # Target Exam
    YEAR = 2024
    EXAM = '행시'
    ROUND = 0

    # Subject full name, field
    HEONBEOB = ('헌법', 'heonbeob')
    EONEO = ('언어논리', 'eoneo')
    JARYO = ('자료해석', 'jaryo')
    SANGHWANG = ('상황판단', 'sanghwang')
    PSAT_TOTAL = ('PSAT 총점', 'psat')
    PSAT_AVG = ('PSAT 평균', 'psat_avg')

    # Subject variables dictionary
    SUBJECT_VARS = {
        '헌법': HEONBEOB,
        '언어': EONEO,
        '자료': JARYO,
        '상황': SANGHWANG,
        '총점': PSAT_TOTAL,
        '평균': PSAT_AVG,
    }
    FIELD_VARS = {
        'heonbeob': '헌법',
        'eoneo': '언어',
        'jaryo': '자료',
        'sanghwang': '상황',
        'psat_total': '총점',
        'psat_avg': '평균',
    }

    # Customize PROBLEM_COUNT, SUBJECT_VARS by Exam
    if EXAM == '칠급':
        PROBLEM_COUNT = {'eoneo': 25, 'jaryo': 25, 'sanghwang': 25}
        SUBJECT_VARS.pop('헌법')
    else:
        PROBLEM_COUNT = {'heonbeob': 25, 'eoneo': 40, 'jaryo': 40, 'sanghwang': 40}

    # Answer file
    ANSWER_FILE = settings.BASE_DIR / 'a_predict/data/answers.csv'
    EMPTY_FILE = settings.BASE_DIR / 'a_predict/data/answers_empty.csv'
    ANSWER_FILE = ANSWER_FILE if os.path.exists(ANSWER_FILE) else EMPTY_FILE
    ANSWER_FILE_ENCODING = detect_encoding(ANSWER_FILE)

    # View info
    INFO = {
        'menu': 'predict',
        'view_type': 'predict',
    }

    # Queryset variables
    qs_exam = Exam.objects.filter(exam=EXAM, round=ROUND)
    qs_unit = Unit.objects.filter(exam=EXAM)
    qs_department = Department.objects.filter(exam=EXAM)
    qs_location = Location.objects.filter(year=YEAR, exam=EXAM)
    qs_student = Student.objects.filter(year=YEAR, exam=EXAM, round=ROUND)
    qs_student_answer = StudentAnswer.objects.filter(
        student__year=YEAR, student__exam=EXAM, student__round=ROUND)
    qs_submitted_answer = SubmittedAnswer.objects.filter(
        student__year=YEAR, student__exam=EXAM, student__round=ROUND)
    qs_answer_count = AnswerCount.objects.filter(year=YEAR, exam=EXAM, round=ROUND)
    qs_official_answer = OfficialAnswer.objects.filter(year=YEAR, exam=EXAM, round=ROUND)

    def create_student(self, student: Student, request: HtmxHttpRequest) -> Student:
        with transaction.atomic():
            student.year = self.YEAR
            student.exam = self.EXAM
            student.round = self.ROUND
            student.user = request.user
            student.save()
            StudentAnswer.objects.get_or_create(student=student)
            return student

    def get_obj_student(self, request: HtmxHttpRequest) -> Student:
        return self.qs_student.filter(user=request.user).first()

    def get_obj_location(self, student: Student) -> Location:
        serial = int(student.serial)
        return self.qs_location.filter(serial_start__lte=serial, serial_end__gte=serial).first()

    def get_obj_student_answer(self, request: HtmxHttpRequest) -> StudentAnswer:
        return self.qs_student_answer.filter(student__user=request.user).first()

    def get_dict_participants_count(self) -> dict:
        qs_participants_count = self.qs_submitted_answer.values('subject').annotate(
            count=Count('student', distinct=True))
        return {self.SUBJECT_VARS[p['subject']][1]: p['count'] for p in qs_participants_count}

    def get_dict_data_answer_official(self) -> dict:
        # {
        #     '헌법': [
        #         {
        #             'number': 10,
        #             'ans_number': 1,
        #             'ans_number_list': [],
        #             'rate_correct': 0,
        #         },
        #         ...
        #     ]
        # }
        qs_official_answer = self.qs_official_answer.first()
        if qs_official_answer and qs_official_answer.answer:
            return qs_official_answer.answer

        with open(self.ANSWER_FILE, 'r', encoding='utf-8') as f:
            df: DataFrame = pd.read_csv(f, header=0, index_col=0)  # index: 1부터 시작하는 문제 번호

            subjects = ['헌법', '언어', '자료', '상황']
            if '헌법' not in df.columns:
                subjects.remove('헌법')

            data_answer_official = {}
            for subject in subjects:
                df_subject = df[[subject]].dropna()
                field = self.SUBJECT_VARS[subject][1]

                data_answer_official[field] = []
                for index, row in df_subject.iterrows():
                    ans_number = int(row[subject])
                    ans_number_list = [int(ans) for ans in str(ans_number) if ans_number > 5]
                    append_dict = {'number': int(index), 'ans_number': ans_number}
                    if ans_number_list:
                        append_dict['ans_number_list'] = ans_number_list
                    data_answer_official[field].append(append_dict)
            return data_answer_official

    def get_dict_data_answer_rate(self, data_answer_official: dict) -> dict:
        qs_answer_count: QuerySet[AnswerCount] = self.qs_answer_count.order_by('subject', 'number')
        dict_answer_count = {}
        for field in self.PROBLEM_COUNT.keys():
            dict_answer_count[field] = []

        qs: AnswerCount
        for qs in qs_answer_count:
            field = self.SUBJECT_VARS[qs.subject][1]
            answer_official = data_answer_official[field][qs.number - 1]
            ans_official = answer_official['ans']
            qs.rate_correct = getattr(qs, f'rate_{ans_official}')
            answer_official['rate_correct'] = getattr(qs, f'rate_{ans_official}')

            dict_answer_count[field].append(qs)

        return dict_answer_count

    @staticmethod
    def get_list_answer_empty(problem_count: int) -> list:
        answer_empty = []
        for i in range(1, problem_count + 1):
            answer_empty.append({'number': i, 'ans_number': ''})
        return answer_empty

    def get_list_answer_temp(
            self,
            request: HtmxHttpRequest,
            sub: str,
            queryset: SubmittedAnswer | None = None
    ) -> list:
        problem_count: int = self.PROBLEM_COUNT[sub]
        answer_temp: list = self.get_list_answer_empty(problem_count=problem_count)
        if queryset is None:
            queryset = self.qs_submitted_answer.filter(student__user=request.user)
        for qs in queryset:
            qs: SubmittedAnswer
            if qs.subject == sub:
                answer_temp[qs.number - 1] = {'no': qs.number, 'ans': qs.answer}
        return answer_temp

    def get_tuple_data_answer_student(
            self, request: HtmxHttpRequest,
            data_answer_rate: dict,
    ) -> tuple[dict[str, list], dict[str, int], dict[str, bool]]:
        qs_answer_final: StudentAnswer = self.get_obj_student_answer(request=request)
        qs_answer_temp: QuerySet[SubmittedAnswer] = self.qs_submitted_answer.filter(student__user=request.user)

        data_answer_student: dict[str, list] = qs_answer_final.answer
        data_answer_count: dict[str, int] = qs_answer_final.answer_count
        data_answer_confirmed: dict[str, bool] = qs_answer_final.answer_confirmed

        for field, value in data_answer_student.items():
            for answer_student in value:
                number = answer_student['no']
                ans_number = answer_student['ans']
                answer_rate: AnswerCount = data_answer_rate[field][number - 1]
                answer_student['rate_selection'] = getattr(answer_rate, f'rate_{ans_number}')

        return data_answer_student, data_answer_count, data_answer_confirmed

    def create_submitted_answer(self, request: HtmxHttpRequest, sub: str) -> SubmittedAnswer:
        student = self.get_obj_student(request=request)
        number = request.POST.get('number')
        answer = request.POST.get('answer')
        with transaction.atomic():
            submitted_answer, _ = SubmittedAnswer.objects.get_or_create(student=student, subject=sub, number=number)
            submitted_answer.answer = answer
            submitted_answer.save()
            submitted_answer.refresh_from_db()
            return submitted_answer

    def get_tuple_answer_string_confirm(self, request: HtmxHttpRequest, sub: str) -> tuple[str, bool]:
        answer_temp: list = self.get_list_answer_temp(request=request, sub=sub)
        is_confirmed = True

        answer_list: list[str] = []
        for answer in answer_temp:
            ans_number = answer['ans_number']
            if ans_number == '':
                is_confirmed = False
            else:
                answer_list.append(str(ans_number))
        answer_string = ','.join(answer_list) if is_confirmed else ''
        return answer_string, is_confirmed

    def get_str_next_url(self, student_answer: StudentAnswer) -> str:
        for sub in self.PROBLEM_COUNT.keys():
            field = self.SUBJECT_VARS[sub][1]
            is_confirmed = getattr(student_answer, f'{field}_confirmed')
            if not is_confirmed:
                return reverse_lazy('predict:answer-input', args=[sub])
        return reverse_lazy('predict_test:index')

    def get_answer_predict(self, data_answer_correct):
        data_answer_predict = {}
        qs_submitted_answers = ''

        for sub, problem_count in self.PROBLEM_COUNT.items():
            answers_predict = self.get_list_answer_empty(problem_count=problem_count)
            for i in range(1, problem_count + 1):
                ans_number_correct = data_answer_correct[sub][i - 1]['ans_number']
                answer_count_list = []  # list for counting answers
                for i in range(5):
                    answer_count_list.append(problem[f'count_{i + 1}'])
                ans_number_predict = answer_count_list.index(max(answer_count_list)) + 1  # 예상 정답
                rate_accuracy = problem[f'rate_{ans_number_predict}']  # 정확도

                result = 'O'
                if ans_number_correct and ans_number_correct != ans_number_predict:
                    result = 'X'
                data_answer_predict[sub].append(
                    {
                        'number': number,
                        'ans_number': ans_number_predict,
                        'result': result,
                        'rate_accuracy': rate_accuracy,
                    }
                )

    def get_dict_info_answer_student_empty(self, field):
        sub = self.FIELD_VARS[field]
        return {
            'icon': icon_set.ICON_SUBJECT[sub],
            'sub': sub,
            'subject': self.SUBJECT_VARS[sub][0],
            'sub_eng': self.SUBJECT_VARS[sub][1],
        }

    def get_dict_info_answer_student(
            self,
            data_answer_student: dict,
            data_answer_count: dict,
            data_answer_confirmed: dict,
            data_answer_official: dict,
    ) -> dict:
        participants_count = self.get_dict_participants_count()
        info_answer_student = {}
        if data_answer_student:
            total_score_real = 0
            for field, value in data_answer_student.items():
                problem_count = self.PROBLEM_COUNT[field]
                answer_count = data_answer_count[field]
                is_confirmed = data_answer_confirmed[field]

                try:
                    participants = participants_count[field]
                except KeyError:
                    participants = 0

                correct_count = 0
                for idx, answer_student in enumerate(value):
                    ans_student = answer_student['ans']
                    ans_official = data_answer_official[field][idx]['ans']

                    try:
                        ans_official_list = data_answer_official[field][idx]['ans_list']
                    except KeyError:
                        ans_official_list = None

                    result = 'X'
                    if ans_official_list and ans_student in ans_official_list:
                        result = 'O'
                    if ans_student == ans_official:
                        result = 'O'
                    answer_student['result'] = result
                    correct_count += 1 if result == 'O' else 0

                score_real = correct_count * 100 / problem_count
                total_score_real += score_real

                info_answer_student[field] = self.get_dict_info_answer_student_empty(field)
                info_answer_student[field].update({
                    'problem_count': problem_count,
                    'participants': participants,
                    'answer_count': answer_count,
                    # 'score_virtual': score_virtual[sub],
                    'score_real': correct_count * 100 / problem_count,
                    'is_confirmed': is_confirmed,
                })

            info_answer_student['psat_avg'] = self.get_dict_info_answer_student_empty('psat_avg')
            info_answer_student['psat_avg'].update({
                'participants': participants_count[max(participants_count)],
                'problem_count': sum([val for val in self.PROBLEM_COUNT.values()]),
                'answer_count': sum([val for val in data_answer_count.values()]),
                # 'score_virtual': score_virtual[sub],
                'score_real': total_score_real / len(self.PROBLEM_COUNT),
                'is_confirmed': all(data_answer_confirmed),
            })
        return info_answer_student
