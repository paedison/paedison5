import os

import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from a_common import utils as common_utils
from a_common.constants import icon_set
from a_predict import forms as predict_forms
from a_predict import models as predict_models

CURRENT_YEAR = 2024
CURRENT_EXAM = '행시'
CURRENT_ROUND = 0

# answer_file
DATA_DIR = os.path.join(settings.BASE_DIR, 'a_predict', 'data')
ANSWER_FILE = os.path.join(DATA_DIR, 'answers.csv')
ANSWER_EMPTY_FILE = os.path.join(DATA_DIR, 'answers_empty.csv')

qs_exam = predict_models.Exam.objects.filter(exam=CURRENT_EXAM)
qs_unit = predict_models.Unit.objects.filter(exam=CURRENT_EXAM)
qs_department = predict_models.Department.objects.filter(exam=CURRENT_EXAM)
qs_student = predict_models.Student.objects.filter(
    year=CURRENT_YEAR, exam=CURRENT_EXAM, round=CURRENT_ROUND)

sub_eng_dict = {
    '헌법': 'heonbeob',
    '언어': 'eoneo',
    '자료': 'jaryo',
    '상황': 'sanghwang',
    '피셋': 'psat',
}
subject_dict = {
    '헌법': '헌법',
    '언어': '언어논리',
    '자료': '자료해석',
    '상황': '상황판단',
    '피셋': 'PSAT 평균',
}
sub_field = {
    '헌법': 'score_heonbeob',
    '언어': 'score_eoneo',
    '자료': 'score_jaryo',
    '상황': 'score_sanghwang',
    'psat': 'score_psat',
    'psat_avg': 'score_psat_avg',
}


def get_answer_correct(file):
    df = pd.read_csv(file, header=0, index_col=0)

    subjects = ['헌법', '언어', '자료', '상황']
    if '헌법' not in df.columns:
        subjects.remove('헌법')

    answer_correct = {}
    for subject in subjects:
        filtered_df = df[[subject]].dropna()

        answer_correct[subject] = []
        for index, row in filtered_df.iterrows():
            ans_number = int(row[subject])
            ans_number_list = [
                int(ans) for ans in str(ans_number) if ans_number > 5
            ]
            append_dict = {'number': int(index), 'ans_number': ans_number}
            if ans_number_list:
                append_dict['ans_number_list'] = ans_number_list
            answer_correct[subject].append(append_dict)
    return answer_correct


def get_answer_correct_dict() -> dict:
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
    try:
        with open(ANSWER_FILE, 'r', encoding='utf-8') as file:
            return get_answer_correct(file)
    except FileNotFoundError:
        with open(ANSWER_EMPTY_FILE, 'r', encoding='utf-8') as file:
            return get_answer_correct(file)


def index_view(request: common_utils.HtmxHttpRequest):
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
    location = get_object_or_404(
        predict_models.Location,
        exam=CURRENT_EXAM, serial_start__lte=serial, serial_end__gte=serial)

    answer_correct_dict = get_answer_correct_dict()

    student_answer = predict_models.StudentAnswer.objects.filter(student=student)
    data_answer_student = {}
    if student_answer:
        data_answer_student = student_answer.first().answer_dict

    info_answer_student = {}
    if data_answer_student:
        problem_count = 25 if CURRENT_EXAM == '칠급' else 40
        for sub, answer in data_answer_student.items():
            info_answer_student[sub] = {
                'icon': icon_set.ICON_SUBJECT[sub],
                'sub': sub,
                'sub_eng': sub_eng_dict[sub],
                'subject': subject_dict[sub],
                # 'participants': self.participant_count[sub],
                'problem_count': 25 if sub == '헌법' else problem_count,
                'answer_count': len(data_answer_student),
                # 'score_virtual': score_virtual[sub],
                # 'score_real': None,
                'is_confirmed': len(data_answer_student) > 0,
            }

    context = common_utils.update_context_data(
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
        data_answer_correct=answer_correct_dict,
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
def student_create_view(request: common_utils.HtmxHttpRequest):
    info = {
        'menu': 'predict',
        'view_type': 'predict',
    }

    form = predict_forms.StudentForm

    departments = qs_department.values_list('department', flat=True).distinct()

    context = common_utils.update_context_data(
        # base info
        info=info,
        exam=CURRENT_EXAM,
        current_time=timezone.now(),

        # icons
        icon_menu=icon_set.ICON_MENU['predict'],
        icon_subject=icon_set.ICON_SUBJECT,
        icon_nav=icon_set.ICON_NAV,

        # index_info_student: 수험 정보
        units=qs_unit,
        departments=departments,
    )

    return render(request, 'a_predict/student_create.html', context)
