from django.contrib import admin

from .models import (
    Exam, Student, StudentAnswer, AnswerCount, Statistics, StatisticsVirtual,
)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'exam',
        'page_opened_at', 'exam_started_at', 'exam_finished_at',
        'answer_predict_opened_at', 'answer_official_opened_at',
    )
    list_per_page = 20


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(StudentAnswer)
class AnswerAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(AnswerCount)
class AnswerCountAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(StatisticsVirtual)
class StatisticsVirtualAdmin(admin.ModelAdmin):
    list_per_page = 20
