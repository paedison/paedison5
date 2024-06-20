import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from a_common.constants import icon_set
from a_common.utils import HtmxHttpRequest, detect_encoding, update_context_data
from a_predict import forms as predict_forms
from a_predict.models import (
    Exam, Unit, Department, Student, Location,
    SubmittedAnswer, StudentAnswer,
    AnswerCount, AnswerCountLowRank, AnswerCountMidRank, AnswerCountTopRank,
    Statistics, StatisticsVirtual,
)
from a_predict.utils import get_answer_correct, get_answer_student

CURRENT_YEAR = 2024
CURRENT_EXAM = '행시'
CURRENT_ROUND = 0

SUBJECT_VARS = {
    '헌법': ('헌법', 'heonbeob'),
    '언어': ('언어논리', 'eoneo'),
    '자료': ('자료해석', 'jaryo'),
    '상황': ('상황판단', 'sanghwang'),
    '총점': ('PSAT 총점', 'psat'),
    '평균': ('PSAT 평균', 'psat_avg'),
}

if CURRENT_EXAM == '칠급':
    PROBLEM_COUNT = {'언어': 25, '자료': 25, '상황': 25}
    SUBJECT_VARS.pop('헌법')
else:
    PROBLEM_COUNT = {'헌법': 25, '언어': 40, '자료': 40, '상황': 40}

# answer_file
ANSWER_FILE = settings.BASE_DIR / 'a_predict/data/answers.csv'
EMPTY_FILE = settings.BASE_DIR / 'a_predict/data/answers_empty.csv'
ANSWER_FILE = ANSWER_FILE if os.path.exists(ANSWER_FILE) else EMPTY_FILE
ANSWER_FILE_ENCODING = detect_encoding(ANSWER_FILE)

qs_exam = Exam.objects.filter(exam=CURRENT_EXAM)
qs_unit = Unit.objects.filter(exam=CURRENT_EXAM)
qs_department = Department.objects.filter(exam=CURRENT_EXAM)
qs_student = Student.objects.filter(
    year=CURRENT_YEAR, exam=CURRENT_EXAM, round=CURRENT_ROUND)
qs_location = Location.objects.filter(year=CURRENT_YEAR, exam=CURRENT_EXAM)
qs_student_answer = StudentAnswer.objects
qs_submitted_answer = SubmittedAnswer.objects


def index_view(request: HtmxHttpRequest):
    context = {}

    if not request.user.is_authenticated:
        return render(request, 'a_predict/normal/predict_index.html', context)

    student = qs_student.filter(user=request.user).first()
    if not student:
        return redirect('predict:student-create')

    info = {
        'menu': 'predict',
        'view_type': 'predict',
    }

    serial = int(student.serial)
    location = qs_location.filter(serial_start__lte=serial, serial_end__gte=serial).first()

    data_answer_correct = get_answer_correct(ANSWER_FILE)

    qs_answer_final = qs_student_answer.filter(student=student).first()
    qs_answer_temp = qs_submitted_answer.filter(student=student)
    data_answer_student, data_answer_count = get_answer_student(
        qs_answer_final, qs_answer_temp, SUBJECT_VARS, PROBLEM_COUNT)

    psat_problem_count = sum([val for val in PROBLEM_COUNT.values()])
    psat_answer_count = sum([val for val in data_answer_count.values()])

    info_answer_student = {}
    if data_answer_student:
        for sub, answer in data_answer_student.items():
            subject, sub_eng = SUBJECT_VARS[sub]
            problem_count = PROBLEM_COUNT[sub]

            answer_count = data_answer_count[sub]
            is_confirmed = getattr(qs_answer_final, f'{sub_eng}_confirmed')

            info_answer_student[sub] = {
                'icon': icon_set.ICON_SUBJECT[sub],
                'sub': sub,
                'sub_eng': sub_eng,
                'subject': subject,
                # 'participants': self.participant_count[sub],
                'problem_count': problem_count,
                'answer_count': answer_count,
                # 'score_virtual': score_virtual[sub],
                # 'score_real': None,
                'is_confirmed': is_confirmed,
            }

        info_answer_student['평균'] = {
            'icon': '',
            'sub': '평균',
            'sub_eng': 'psat_avg',
            'subject': 'PSAT 평균',
            # 'participants': self.participant_count[sub],
            'problem_count': psat_problem_count,
            'answer_count': psat_answer_count,
            # 'score_virtual': score_virtual[sub],
            # 'score_real': None,
            'is_confirmed': qs_answer_final.all_confirmed,
        }

    context = update_context_data(
        context,

        # base info
        info=info,
        exam=CURRENT_EXAM,
        current_time=timezone.now(),

        # icons
        icon_menu=icon_set.ICON_MENU['predict'],
        icon_subject=icon_set.ICON_SUBJECT,
        icon_nav=icon_set.ICON_NAV,

        # index_info_student: 수험 정보
        student=student,
        location=location,

        # index_info_answer: 답안 제출 현황
        info_answer_student=info_answer_student,

        # index_sheet_answer: 답안 확인
        data_answer_correct=data_answer_correct,
        # data_answer_predict=data_answer['answer_predict'],
        data_answer_student=data_answer_student,

        # index_sheet_score: 성적 예측 I [전체 데이터]
        # score_student=score_student,
        # all_score_stat=all_score_stat,

        # index_sheet_score_filtered: 성적 예측 II [정답 공개 전 데이터]
        # filtered_score_student=filtered_score_student,
        # filtered_all_score_stat=filtered_all_score_stat,
    )
    return render(request, 'a_predict/normal/predict_index.html', context)


@login_required
def student_create_view(request: HtmxHttpRequest):
    student = qs_student.filter(user=request.user).first()
    if student:
        return redirect('predict:index')

    info = {
        'menu': 'predict',
        'view_type': 'predict',
    }
    if request.method == "POST":
        form = predict_forms.StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.year = CURRENT_YEAR
            student.exam = CURRENT_EXAM
            student.round = CURRENT_ROUND
            student.user = request.user
            student.save()
            qs_student_answer.get_or_create(student=student)
        else:
            pass
        return redirect('predict:index')

    else:
        form = predict_forms.StudentForm()

    context = update_context_data(
        # base info
        info=info,
        exam=CURRENT_EXAM,
        current_time=timezone.now(),

        # icons
        icon_menu=icon_set.ICON_MENU['predict'],
        icon_subject=icon_set.ICON_SUBJECT,
        icon_nav=icon_set.ICON_NAV,

        # index_info_student: 수험 정보
        units=qs_unit.values_list('unit', flat=True),
        form=form,
    )

    return render(request, 'a_predict/student_create.html', context)


@login_required
def department_list(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        departments = qs_department.filter(unit=unit).values_list('department', flat=True)
        context = update_context_data(departments=departments)
        return render(request, 'a_predict/snippets/department_list.html', context)
