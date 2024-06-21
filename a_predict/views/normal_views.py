from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from a_common.constants import icon_set
from a_common.utils import HtmxHttpRequest, update_context_data
from a_predict import forms as predict_forms
from .base_info import ExamInfo


def index_view(request: HtmxHttpRequest):
    ei = ExamInfo()
    context = {}

    if not request.user.is_authenticated:
        return render(request, 'a_predict/index.html', context)

    student = ei.get_student(request=request)
    if not student:
        return redirect('predict:student-create')

    info = {
        'menu': 'predict',
        'view_type': 'predict',
    }

    serial = int(student.serial)
    location = ei.get_location(serial=serial)

    data_answer_correct = ei.get_answer_correct()
    data_answer_student, data_answer_count, data_answer_confirmed = ei.get_answer_student(student=student)

    participants_count = ei.get_participants()
    problem_count = ei.PROBLEM_COUNT

    info_answer_student = {}
    if data_answer_student:
        for sub, answer in data_answer_student.items():
            info_answer_student[sub] = {
                'icon': icon_set.ICON_SUBJECT[sub],
                'sub': sub,
                'subject': ei.SUBJECT_VARS[sub][0],
                'sub_eng': ei.SUBJECT_VARS[sub][1],
                'participants': participants_count[sub],
                'problem_count': problem_count[sub],
                'answer_count': data_answer_count[sub],
                # 'score_virtual': score_virtual[sub],
                # 'score_real': None,
                'is_confirmed': data_answer_confirmed[sub],
            }

        info_answer_student['평균'] = {
            'icon': '',
            'sub': '평균',
            'sub_eng': 'psat_avg',
            'subject': 'PSAT 평균',
            'participants': max(participants_count),
            'problem_count': sum([val for val in problem_count.values()]),
            'answer_count': sum([val for val in data_answer_count.values()]),
            # 'score_virtual': score_virtual[sub],
            # 'score_real': None,
            'is_confirmed': all(data_answer_confirmed),
        }

    context = update_context_data(
        context,

        # base info
        info=info,
        exam=ei.EXAM,
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
    return render(request, 'a_predict/index.html', context)


@login_required
def student_create_view(request: HtmxHttpRequest):
    ei = ExamInfo()
    student = ei.get_student(request=request)
    if student:
        return redirect('predict:index')

    if request.method == "POST":
        form = predict_forms.StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            ei.create_student(student=student, request=request)
        else:
            pass
        first_sub = '헌법' if '헌법' in ei.PROBLEM_COUNT.keys() else '언어'
        return redirect('predict:answer-input', first_sub)

    else:
        form = predict_forms.StudentForm()

    units = ei.qs_unit.values_list('unit', flat=True)
    context = update_context_data(
        # base info
        info=ei.INFO,
        exam=ei.EXAM,
        current_time=timezone.now(),

        # icons
        icon_menu=icon_set.ICON_MENU['predict'],
        icon_subject=icon_set.ICON_SUBJECT,
        icon_nav=icon_set.ICON_NAV,

        # index_info_student: 수험 정보
        units=units,
        form=form,
    )

    return render(request, 'a_predict/student_create.html', context)


@login_required
def department_list(request):
    if request.method == 'POST':
        ei = ExamInfo()
        unit = request.POST.get('unit')
        departments = ei.qs_department.filter(unit=unit).values_list('department', flat=True)
        context = update_context_data(departments=departments)
        return render(request, 'a_predict/snippets/department_list.html', context)


@login_required
def answer_input_view(request, sub):
    ei = ExamInfo()

    problem_count = ei.PROBLEM_COUNT
    if sub not in problem_count.keys():
        return redirect('predict:index')

    student = ei.get_student(request=request)
    if not student:
        return redirect('predict:student-create')

    field = ei.SUBJECT_VARS[sub][1]
    qs_answer_final = ei.get_qs_student_answer(student=student)
    is_confirmed = getattr(qs_answer_final, f'{field}_confirmed')
    if is_confirmed:
        return redirect('predict:index')

    answer_student_list = []
    answer_temp = ei.get_answer_temp(student=student, sub=sub)
    for i in range(problem_count[sub]):
        number = i + 1
        answer_student_list.append({
            'number': number,
            # 'ex': ei.EXAM,
            'sub': sub,
            'answer_student': answer_temp[i]['ans_number'],
        })

    context = update_context_data(
        # base info
        info=ei.INFO,
        exam=ei.EXAM,
        sub=sub,
        answer_student=answer_student_list,
    )
    return render(request, 'a_predict/answer_input.html', context)


@login_required
def answer_submit(request, sub):
    if request.method == 'POST':
        ei = ExamInfo()
        submitted_answer = ei.create_submitted_answer(request, sub)
        context = update_context_data(sub=sub, submitted_answer=submitted_answer)
        return render(request, 'a_predict/snippets/scored_form.html', context)


@login_required
def answer_confirm(request, sub):
    if request.method == 'POST':
        ei = ExamInfo()
        subject, field = ei.SUBJECT_VARS[sub]

        student = ei.get_student(request=request)
        is_confirmed, ans_number_list = ei.get_data_answer_confirmed(student=student, sub=sub)

        student_answer = ei.get_qs_student_answer(student=student)
        if is_confirmed:
            answer_string = ','.join(ans_number_list)
            setattr(student_answer, field, answer_string)
            setattr(student_answer, f'{field}_confirmed', is_confirmed)
            student_answer.save()

        next_url = ei.get_next_url(student_answer=student_answer)

        context = update_context_data(
            header=f'{subject} 답안 제출',
            is_confirmed=is_confirmed,
            next_url=next_url,
        )
        return render(request, 'a_predict/snippets/modal_answer_confirmed.html', context)
    else:
        return redirect('predict:answer-input', sub)
