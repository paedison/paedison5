import pandas as pd
import os

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.urls import reverse_lazy

from a_common.utils import detect_encoding, HtmxHttpRequest
from a_predict.models import Student, Location, StudentAnswer, SubmittedAnswer, Unit, Department


class ExamInfo:
    # Target Exam
    YEAR = 2025
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

    # Customize PROBLEM_COUNT, SUBJECT_VARS by Exam
    if EXAM == '칠급':
        PROBLEM_COUNT = {'언어': 25, '자료': 25, '상황': 25}
        SUBJECT_VARS.pop('헌법')
    else:
        PROBLEM_COUNT = {'헌법': 25, '언어': 40, '자료': 40, '상황': 40}

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
    qs_unit = Unit.objects.filter(exam=EXAM)
    qs_department = Department.objects.filter(exam=EXAM)
    qs_location = Location.objects.filter(year=YEAR, exam=EXAM)
    qs_student = Student.objects.filter(year=YEAR, exam=EXAM, round=ROUND)
    qs_student_answer = StudentAnswer.objects
    qs_submitted_answer = SubmittedAnswer.objects

    def create_student(self, student: Student, request: HtmxHttpRequest) -> Student:
        with transaction.atomic():
            student.year = self.YEAR
            student.exam = self.EXAM
            student.round = self.ROUND
            student.user = request.user
            student.save()
            StudentAnswer.objects.get_or_create(student=student)
            return student

    def get_student(self, request: HtmxHttpRequest) -> Student:
        return self.qs_student.filter(user=request.user).first()

    def get_location(self, serial: int) -> Location:
        return self.qs_location.filter(serial_start__lte=serial, serial_end__gte=serial).first()

    def get_qs_student_answer(self, student: Student) -> StudentAnswer:
        return self.qs_student_answer.filter(student=student).first()

    def get_submitted_answer(self, student: Student) -> SubmittedAnswer:
        return self.qs_submitted_answer.filter(student=student)

    def get_participants(self) -> dict:
        def get_participants_by_subject(subject: str) -> int:
            return SubmittedAnswer.objects.filter(
                student__year=self.YEAR, student__exam=self.EXAM, student__round=self.ROUND, subject=subject,
            ).values_list('student').distinct().count()

        participants_count = {}
        for sub in self.PROBLEM_COUNT.keys():
            participants_count[sub] = get_participants_by_subject(sub)

        return participants_count

    def get_answer_correct(self) -> dict:
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
        with open(self.ANSWER_FILE, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f, header=0, index_col=0)

            subjects = ['헌법', '언어', '자료', '상황']
            if '헌법' not in df.columns:
                subjects.remove('헌법')

            answer_correct = {}
            for subject in subjects:
                df_subject = df[[subject]].dropna()

                answer_correct[subject] = []
                for index, row in df_subject.iterrows():
                    ans_number = int(row[subject])
                    ans_number_list = [int(ans) for ans in str(ans_number) if ans_number > 5]
                    append_dict = {'number': int(index), 'ans_number': ans_number}
                    if ans_number_list:
                        append_dict['ans_number_list'] = ans_number_list
                    answer_correct[subject].append(append_dict)
            return answer_correct

    def get_answer_temp(self, student: Student, sub: str) -> list:
        problem_count = self.PROBLEM_COUNT[sub]

        answers_temp = []
        for i in range(problem_count):
            answers_temp.append({'number': i + 1, 'ans_number': ''})

        submitted_answer = SubmittedAnswer.objects.filter(
            student=student, subject=sub).order_by('number').values('number', ans_number=F('answer'))
        for ans in submitted_answer:
            index = ans['number'] - 1
            answers_temp[index]['ans_number'] = ans['ans_number']
        return answers_temp

    def get_answer_student(self, student: Student) -> tuple[dict, dict, dict]:
        qs_answer_final = self.get_qs_student_answer(student=student)
        qs_answer_temp = self.get_submitted_answer(student=student)

        def get_answer_student_by_subject(subject: str) -> tuple[list, int, bool]:
            field = self.SUBJECT_VARS[subject][1]
            is_confirmed = getattr(qs_answer_final, f'{field}_confirmed')
            if is_confirmed:
                answer_final = qs_answer_final.get_answer_list(field)
                return answer_final, len(answer_final), is_confirmed
            else:
                answers_temp = []
                for i in range(1, self.PROBLEM_COUNT[subject] + 1):
                    answers_temp.append({'number': i, 'ans_number': ''})

                submitted_answer = qs_answer_temp.filter(subject=subject).values(
                    'number', ans_number=F('answer'))
                for ans in submitted_answer:
                    index = ans['number'] - 1
                    answers_temp[index]['ans_number'] = ans['ans_number']
                return answers_temp, len(submitted_answer), is_confirmed

        answer_student = {}
        answer_count = {}
        answer_confirmed = {}
        for sub in self.PROBLEM_COUNT.keys():
            answer_student[sub], answer_count[sub], answer_confirmed[sub] = get_answer_student_by_subject(sub)

        return answer_student, answer_count, answer_confirmed

    def create_submitted_answer(self, request: HtmxHttpRequest, sub: str) -> SubmittedAnswer:
        student = self.qs_student.filter(user=request.user).first()
        number = request.POST.get('number')
        answer = request.POST.get('answer')
        with transaction.atomic():
            submitted_answer, _ = SubmittedAnswer.objects.get_or_create(student=student, subject=sub, number=number)
            submitted_answer.answer = answer
            submitted_answer.save()
            submitted_answer.refresh_from_db()
            return submitted_answer

    def get_data_answer_confirmed(self, student: Student, sub: str) -> tuple[bool, list]:
        answer_temp = self.get_answer_temp(student=student, sub=sub)
        is_confirmed = True
        ans_number_list = []

        for answer in answer_temp:
            ans_number = answer['ans_number']
            ans_number_list.append(ans_number)
            if ans_number == '':
                is_confirmed = False

        return is_confirmed, ans_number_list

    def confirm_answer_student(self):
        pass

    def get_next_url(self, student_answer: StudentAnswer):
        sub_list = self.PROBLEM_COUNT.keys()
        for sub in sub_list:
            field = self.SUBJECT_VARS[sub][1]
            is_confirmed = getattr(student_answer, f'{field}_confirmed')
            if not is_confirmed:
                return reverse_lazy('predict:answer-input', args=[sub])
        return reverse_lazy('predict_test:index')
