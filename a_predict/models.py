import os
from datetime import datetime

import pytz
from django.conf import settings
from django.db import models
from django.utils import timezone

from a_common.models import User

data_dir = os.path.join(settings.BASE_DIR, 'predict', 'models', 'data')


current_year = datetime.now().year


def year_choice() -> list:
    choice = [(year, f'{year}년') for year in range(2004, current_year + 1)]
    choice.reverse()
    return choice


def number_choice() -> list:
    return [(number, f'{number}번') for number in range(1, 41)]


def get_remarks(message_type: str, remarks: str | None) -> str:
    utc_now = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M')
    separator = '|' if remarks else ''
    if message_type:
        if remarks:
            remarks += f"{separator}{message_type}_at:{utc_now}"
        else:
            remarks = f"{message_type}_at:{utc_now}"
        return remarks


class ExamChoice(models.TextChoices):
    HAENGSI = '행시', '5급공채/외교원/지역인재 7급'
    IPSI = '입시', '입법고시'
    CHILGEUP = '칠급', '7급공채/민간경력 5·7급'
    PRIME = '프모', '프라임 모의고사'


class SubjectChoice(models.TextChoices):
    HEONBEOB = '헌법', '헌법'
    EONEO = '언어', '언어논리'
    JARYO = '자료', '자료해석'
    SANGHWANG = '상황', '상황판단'


class ChoiceMethod:
    @staticmethod
    def get_exam_choices():
        return ExamChoice.choices

    @staticmethod
    def get_subject_choices():
        return SubjectChoice.choices


class TimeRecordField(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class RemarksField(models.Model):
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk is not None:
            message_type = kwargs.pop('message_type', '')
            self.remarks = get_remarks(message_type, self.remarks)
        super().save(*args, **kwargs)


class TimeRemarkChoiceBase(TimeRecordField, RemarksField, ChoiceMethod):
    class Meta:
        abstract = True


class TimeChoiceBase(TimeRecordField, ChoiceMethod):
    class Meta:
        abstract = True


class Exam(TimeRemarkChoiceBase):
    exam = models.CharField(max_length=2, choices=ExamChoice)
    round = models.IntegerField(default=0)  # 0 for '행시, 입시, 칠급', round number for '프모'

    page_opened_at = models.DateTimeField(default=timezone.now)
    exam_started_at = models.DateTimeField(default=timezone.now)
    exam_finished_at = models.DateTimeField(default=timezone.now)
    answer_predict_opened_at = models.DateTimeField(default=timezone.now)
    answer_official_opened_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['exam', 'round']

    def __str__(self):
        return self.exam

    # @property
    # def answer_file(self):
    #     return os.path.join(data_dir, f"answer_file_{self.category}_{self.year}{self.ex}-{self.round}.csv")


class Unit(TimeRemarkChoiceBase):
    exam = models.CharField(max_length=2, choices=ExamChoice)
    unit = models.CharField(max_length=128)
    order = models.IntegerField()

    class Meta:
        unique_together = ['exam', 'unit']
        ordering = ['order']

    def __str__(self):
        return f'{self.exam}-{self.unit}'


class Department(TimeRemarkChoiceBase):
    exam = models.CharField(max_length=2, choices=ExamChoice)
    unit = models.CharField(max_length=128)
    department = models.CharField(max_length=128)
    order = models.IntegerField()

    class Meta:
        unique_together = ['exam', 'unit', 'department']
        ordering = ['order']

    def __str__(self):
        return f'{self.exam}-{self.unit}-{self.department}'


class Student(TimeRemarkChoiceBase):
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice)
    round = models.IntegerField(default=0)  # 0 for '행시, 입시, 칠급', round number for '프모'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='psat_predict_students')
    name = models.CharField(max_length=20)
    serial = models.CharField(max_length=10)
    unit = models.CharField(max_length=128)
    department = models.CharField(max_length=128)

    password = models.IntegerField()
    prime_id = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "성적 예측 수험 정보"
        verbose_name_plural = "성적 예측 수험 정보"
        unique_together = ['year', 'exam', 'round', 'user']

    def __str__(self):
        return f'{self.year}{self.exam}{self.round}({self.unit}-{self.department})_{self.user.username}'


class SubmittedAnswer(TimeRemarkChoiceBase):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submitted_answers')
    subject = models.CharField(max_length=2, choices=SubjectChoice)
    number = models.IntegerField(choices=number_choice, default=1)
    answer = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'subject', 'number']
        db_table = 'a_predict_submitted_answer'


class StudentAnswer(TimeRemarkChoiceBase):
    updated_at = models.DateTimeField(auto_now=True)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='student_answers')

    heonbeob = models.TextField(default='')
    eoneo = models.TextField(default='')
    jaryo = models.TextField(default='')
    sanghwang = models.TextField(default='')

    heonbeob_confirmed = models.BooleanField(default=False)
    eoneo_confirmed = models.BooleanField(default=False)
    jaryo_confirmed = models.BooleanField(default=False)
    sanghwang_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "성적 예측 제출 답안"
        verbose_name_plural = "성적 예측 제출 답안"
        db_table = 'a_predict_student_answer'

    def __str__(self):
        return f'[Answer#{self.id}]{self.student}'

    @property
    def all_confirmed(self):
        confirmed_list = [self.eoneo_confirmed, self.jaryo_confirmed, self.sanghwang_confirmed]
        if self.student.exam != '칠급':
            confirmed_list.append(self.heonbeob_confirmed)
        return all(confirmed_list)

    def get_answer_list(self, subject_field: str) -> list[dict]:
        ans_str: str = getattr(self, subject_field)
        ans_str_list = ans_str.split(',') if ans_str else []
        answer_list = []
        for idx, val in enumerate(ans_str_list):
            ans_number = int(val)
            ans_number_list = [int(v) for v in val if ans_number > 5]
            append_dict = {'number': idx + 1, 'ans_number': ans_number}
            if ans_number_list:
                append_dict['ans_number_list'] = ans_number_list
            answer_list.append(append_dict)
        return answer_list

    @property
    def answer_dict(self):
        return {
            '헌법': self.get_answer_list('heonbeob'),
            '언어': self.get_answer_list('eoneo'),
            '자료': self.get_answer_list('jaryo'),
            '상황': self.get_answer_list('sanghwang'),
        }


# class StudentAnswer(TimeRemarkChoiceBase):
#     student = models.OneToOneField(PredictStudent, on_delete=models.CASCADE, related_name='answers')
#     subject = models.CharField(max_length=2, choices=SubjectChoice)
#     is_confirmed = models.BooleanField(default=False)
#     prob1 = models.IntegerField(blank=True, null=True)
#     prob2 = models.IntegerField(blank=True, null=True)
#     prob3 = models.IntegerField(blank=True, null=True)
#     prob4 = models.IntegerField(blank=True, null=True)
#     prob5 = models.IntegerField(blank=True, null=True)
#     prob6 = models.IntegerField(blank=True, null=True)
#     prob7 = models.IntegerField(blank=True, null=True)
#     prob8 = models.IntegerField(blank=True, null=True)
#     prob9 = models.IntegerField(blank=True, null=True)
#     prob10 = models.IntegerField(blank=True, null=True)
#     prob11 = models.IntegerField(blank=True, null=True)
#     prob12 = models.IntegerField(blank=True, null=True)
#     prob13 = models.IntegerField(blank=True, null=True)
#     prob14 = models.IntegerField(blank=True, null=True)
#     prob15 = models.IntegerField(blank=True, null=True)
#     prob16 = models.IntegerField(blank=True, null=True)
#     prob17 = models.IntegerField(blank=True, null=True)
#     prob18 = models.IntegerField(blank=True, null=True)
#     prob19 = models.IntegerField(blank=True, null=True)
#     prob20 = models.IntegerField(blank=True, null=True)
#     prob21 = models.IntegerField(blank=True, null=True)
#     prob22 = models.IntegerField(blank=True, null=True)
#     prob23 = models.IntegerField(blank=True, null=True)
#     prob24 = models.IntegerField(blank=True, null=True)
#     prob25 = models.IntegerField(blank=True, null=True)
#     prob26 = models.IntegerField(blank=True, null=True)
#     prob27 = models.IntegerField(blank=True, null=True)
#     prob28 = models.IntegerField(blank=True, null=True)
#     prob29 = models.IntegerField(blank=True, null=True)
#     prob30 = models.IntegerField(blank=True, null=True)
#     prob31 = models.IntegerField(blank=True, null=True)
#     prob32 = models.IntegerField(blank=True, null=True)
#     prob33 = models.IntegerField(blank=True, null=True)
#     prob34 = models.IntegerField(blank=True, null=True)
#     prob35 = models.IntegerField(blank=True, null=True)
#     prob36 = models.IntegerField(blank=True, null=True)
#     prob37 = models.IntegerField(blank=True, null=True)
#     prob38 = models.IntegerField(blank=True, null=True)
#     prob39 = models.IntegerField(blank=True, null=True)
#     prob40 = models.IntegerField(blank=True, null=True)
#
#     class Meta:
#         verbose_name = "성적 예측 제출 답안"
#         verbose_name_plural = "성적 예측 제출 답안"
#
#     def __str__(self):
#         return f'[Answer#{self.id}]{self.student}_{self.subject}'
#
#
class AnswerCountBase(TimeChoiceBase):
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice)
    round = models.IntegerField(default=0)  # 0 for '행시, 입시, 칠급', round number for '프모'

    subject = models.CharField(max_length=2, choices=SubjectChoice)
    number = models.IntegerField()
    answer = models.IntegerField(null=True, blank=True)

    count_1 = models.IntegerField(default=0)
    count_2 = models.IntegerField(default=0)
    count_3 = models.IntegerField(default=0)
    count_4 = models.IntegerField(default=0)
    count_5 = models.IntegerField(default=0)
    count_0 = models.IntegerField(default=0)
    count_None = models.IntegerField(default=0)

    class Meta:
        abstract = True
        unique_together = ['year', 'exam', 'round', 'subject', 'number']

    def __str__(self):
        class_name = self.__class__.__name__
        return f'[{class_name}#{self.id}]{self.year}{self.exam}{self.round}_{self.subject}-{self.number}'

    @property
    def count_total(self):
        counts = [
            self.count_1, self.count_2, self.count_3, self.count_4, self.count_5,
            self.count_0, self.count_None,
        ]
        return sum(filter(None, counts))

    def get_rate(self, answer: int | None):
        if self.count_total != 0:
            return getattr(self, f'count_{answer}') / self.count_total * 100

    @property
    def rate_0(self):
        return self.get_rate(0)

    @property
    def rate_1(self):
        return self.get_rate(1)

    @property
    def rate_2(self):
        return self.get_rate(2)

    @property
    def rate_3(self):
        return self.get_rate(3)

    @property
    def rate_4(self):
        return self.get_rate(4)

    @property
    def rate_5(self):
        return self.get_rate(5)

    @property
    def rate_None(self):
        return self.get_rate(None)


class AnswerCount(AnswerCountBase):
    class Meta:
        verbose_name = "성적 예측 답안 개수(전체)"
        verbose_name_plural = "성적 예측 답안 개수(전체)"
        db_table = 'a_predict_answer_count'


class AnswerCountTopRank(AnswerCountBase):
    class Meta:
        verbose_name = "성적 예측 답안 개수(상위권)"
        verbose_name_plural = "성적 예측 답안 개수(상위권)"
        db_table = 'a_predict_answer_count_top_rank'


class AnswerCountMidRank(AnswerCountBase):
    class Meta:
        verbose_name = "성적 예측 답안 개수(중위권)"
        verbose_name_plural = "성적 예측 답안 개수(중위권)"
        db_table = 'a_predict_answer_count_mid_rank'


class AnswerCountLowRank(AnswerCountBase):
    class Meta:
        verbose_name = "성적 예측 답안 개수(하위권)"
        verbose_name_plural = "성적 예측 답안 개수(하위권)"
        db_table = 'a_predict_answer_count_low_rank'


class StatisticsBase(TimeRecordField):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)

    score_heonbeob = models.FloatField(null=True, blank=True)
    score_eoneo = models.FloatField(null=True, blank=True)
    score_jaryo = models.FloatField(null=True, blank=True)
    score_sanghwang = models.FloatField(null=True, blank=True)

    rank_total_heonbeob = models.PositiveIntegerField(null=True, blank=True)
    rank_total_eoneo = models.PositiveIntegerField(null=True, blank=True)
    rank_total_jaryo = models.PositiveIntegerField(null=True, blank=True)
    rank_total_sanghwang = models.PositiveIntegerField(null=True, blank=True)
    rank_total_psat = models.PositiveIntegerField(null=True, blank=True)

    rank_department_heonbeob = models.PositiveIntegerField(null=True, blank=True)
    rank_department_eoneo = models.PositiveIntegerField(null=True, blank=True)
    rank_department_jaryo = models.PositiveIntegerField(null=True, blank=True)
    rank_department_sanghwang = models.PositiveIntegerField(null=True, blank=True)
    rank_department_psat = models.PositiveIntegerField(null=True, blank=True)

    rank_ratio_total_heonbeob = models.FloatField(null=True, blank=True)
    rank_ratio_total_eoneo = models.FloatField(null=True, blank=True)
    rank_ratio_total_jaryo = models.FloatField(null=True, blank=True)
    rank_ratio_total_sanghwang = models.FloatField(null=True, blank=True)
    rank_ratio_total_psat = models.FloatField(null=True, blank=True)

    rank_ratio_department_heonbeob = models.FloatField(null=True, blank=True)
    rank_ratio_department_eoneo = models.FloatField(null=True, blank=True)
    rank_ratio_department_jaryo = models.FloatField(null=True, blank=True)
    rank_ratio_department_sanghwang = models.FloatField(null=True, blank=True)
    rank_ratio_department_psat = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        class_name = self.__class__.__name__
        return f'[{class_name}#{self.id}]{self.student}'

    @property
    def score_psat(self):
        score = [self.score_heonbeob, self.score_eoneo, self.score_jaryo, self.score_sanghwang]
        return sum(filter(None, score))

    @property
    def score_psat_avg(self):
        if self.student.exam == '칠급':
            return self.score_psat / 3
        return self.score_psat / 4


class Statistics(StatisticsBase):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='statistics')


class StatisticsVirtual(StatisticsBase):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='statistics_virtual')

    class Meta:
        db_table = 'a_predict_statistics_virtual'


class Location(TimeRemarkChoiceBase):
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice)
    serial_start = models.IntegerField()
    serial_end = models.IntegerField()
    region = models.CharField(max_length=10)
    department = models.CharField(max_length=128)
    school = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    contact = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.region}-{self.department}:{self.school}'
