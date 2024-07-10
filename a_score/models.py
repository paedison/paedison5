import os
from datetime import datetime

import pytz
from django.conf import settings
from django.db import models
from django.utils import timezone

from a_common.models import User

data_dir = os.path.join(settings.BASE_DIR, 'a_score', 'data')

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
    PRIME = '프모', '프라임 PSAT 모의고사'
    PRIMEPOLICE = '프경', '프라임 경위공채 모의고사'


class SubjectChoice(models.TextChoices):
    HEONBEOB = '헌법', '헌법'
    EONEO = '언어', '언어논리'
    JARYO = '자료', '자료해석'
    SANGHWANG = '상황', '상황판단'

    HYEONGSA = '형사', '형사법'
    GYEONGCHAL = '경찰', '경찰학'
    BEOMJOE = '범죄', '범죄학'
    HAENGBEOB = '행법', '행정법'
    HAENGHAG = '행학', '행정학'
    MINBEOB = '민법', '민법총칙'
    SEBEOB = '세법', '세법개론'
    HOEGYE = '회계', '회계학'
    SANGBEOB = '상법', '상법총칙'
    GYEONGJE = '경제', '경제학'
    TONGGYE = '통계', '통계학'
    JAEJEONG = '재정', '재정학'
    JEONGBO = '정보', '정보보호론'
    SINE = '시네', '시스템네트워크보안'
    DEBE = '데베', '데이터베이스론'
    TONGSIN = '통신', '통신이론'
    SOWE = '소웨', '소프트웨어공학'


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
    round = models.IntegerField(default=0)  # 0 for '행시, 입시, 칠급', round number for '프모, 프경'

    page_opened_at = models.DateTimeField(default=timezone.now)
    exam_started_at = models.DateTimeField(default=timezone.now)
    exam_finished_at = models.DateTimeField(default=timezone.now)
    score_opened_at = models.DateTimeField(default=timezone.now)

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


class PrimeStudent(TimeRemarkChoiceBase):
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice)
    round = models.IntegerField(default=0)

    name = models.CharField(max_length=20)
    serial = models.CharField(max_length=10)
    unit = models.CharField(max_length=128)
    department = models.CharField(max_length=128)
    subject = models.JSONField(default=dict)
    password = models.IntegerField()

    class Meta:
        verbose_name = "수험 정보"
        verbose_name_plural = "수험 정보"
        unique_together = ['year', 'exam', 'round', 'serial']
        db_table = 'a_score_prime_student'

    def __str__(self):
        return f'{self.year}{self.exam}{self.round}({self.serial}-{self.name})'


class PrimeStudentRecord(TimeRecordField):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prime_student_records')
    student = models.ForeignKey(PrimeStudent, on_delete=models.CASCADE, related_name='student_records')

    class Meta:
        unique_together = ['user', 'student']
        db_table = 'a_score_prime_student_record'


class PrimeOfficialAnswer(TimeRemarkChoiceBase):
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice)
    round = models.IntegerField(default=0)
    answer = models.JSONField(default=dict)  # answer_official

    class Meta:
        unique_together = ['year', 'exam', 'round']
        db_table = 'a_score_prime_official_answer'


class PrimeStudentAnswer(TimeRemarkChoiceBase):
    student = models.OneToOneField(PrimeStudent, on_delete=models.CASCADE, related_name='student_answers')
    answer = models.JSONField(default=dict)  # answer_student

    class Meta:
        verbose_name = "제출 답안"
        verbose_name_plural = "제출 답안"
        db_table = 'a_score_prime_student_answer'

    def __str__(self):
        return f'[Answer#{self.id}]{self.student}'


class PrimeAnswerCount(TimeChoiceBase):
    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice)
    round = models.IntegerField(default=0)

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
        verbose_name = "성적 예측 답안 개수(전체)"
        verbose_name_plural = "성적 예측 답안 개수(전체)"
        unique_together = ['year', 'exam', 'round', 'subject', 'number']
        db_table = 'a_score_prime_answer_count'

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


class Statistics(TimeRecordField):
    student = models.OneToOneField(PrimeStudent, on_delete=models.CASCADE, related_name='statistics')

    score = models.JSONField(default=dict)
    rank_total = models.JSONField(default=dict)
    rank_department = models.JSONField(default=dict)
    participants_total = models.JSONField(default=dict)
    participants_department = models.JSONField(default=dict)

    def __str__(self):
        return f'[Statistics#{self.id}]{self.student}'
