from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from a_common import utils as common_utils
from a_common.constants import icon_set
from a_predict import models as predict_models
from a_predict import forms as predict_forms

CURRENT_YEAR = 2024
CURRENT_EXAM = '행시'
CURRENT_ROUND = 0

qs_exam = predict_models.Exam.objects.filter(exam=CURRENT_EXAM)
qs_department = predict_models.Department.objects.filter(exam=CURRENT_EXAM)
qs_student = predict_models.Student.objects.filter(
    year=CURRENT_YEAR, exam=CURRENT_EXAM, round=CURRENT_ROUND)


def get_location(student: predict_models.Student):
    if student:
        serial = int(student.serial)
        return get_object_or_404(
            predict_models.Location, exam=CURRENT_EXAM, serial_start__lte=serial, serial_end__gte=serial)


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
    )
    return render(request, 'a_predict/normal/predict_index.html', context)


def student_anonymous_view(request: common_utils.HtmxHttpRequest):
    context = {}
    return render(request, 'a_predict/normal/predict_index.html', context)


@login_required
def student_create_view(request: common_utils.HtmxHttpRequest):
    info = {
        'menu': 'predict',
        'view_type': 'predict',
    }

    form = predict_forms.StudentForm

    units = qs_department.values_list('unit', flat=True).distinct()
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
        units=units,
        departments=departments,
    )

    return render(request, 'a_predict/student_create.html', context)
