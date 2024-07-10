from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone

from a_common.constants import icon_set
from a_common.utils import HtmxHttpRequest, update_context_data
from a_score.models import Exam, PrimeStudent, PrimeStudentRecord


def index_view(request):
    info = {
        'menu': 'score',
        'view_type': 'primeScore',
    }
    exam_list = Exam.objects.filter(exam='프경')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(exam_list, 10)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(number=page_number, on_each_side=3, on_ends=1)

    if request.user.is_authenticated:
        for obj in page_obj:
            student_record: PrimeStudentRecord = PrimeStudentRecord.objects.filter(
                user=request.user, student__exam=obj.exam, student__round=obj.round).first()
            if student_record:
                obj['student'] = student_record.student
                obj['statistics'] = student_record.student.statistics
            # obj['detail_url'] = reverse_lazy('prime:detail', args=[obj['year'], obj['round']])

    context = update_context_data(
        # base info
        info=info,
        current_time=timezone.now(),

        # icons
        icon_menu=icon_set.ICON_MENU['score'],
        icon_subject=icon_set.ICON_SUBJECT,
        # icon_nav=icon_set.ICON_NAV,

        # page objectives
        page_obj=page_obj,
        page_range=page_range,
    )
    return render(request, 'a_score/index.html', context)
