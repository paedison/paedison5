from django.contrib import admin

from .models import (
    Exam, Unit, Department,
    Student, StudentAnswer, SubmittedAnswer,
    AnswerCount, AnswerCountTopRank, AnswerCountMidRank, AnswerCountLowRank,
    Statistics, StatisticsVirtual, Location,
)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'exam',
        'page_opened_at', 'exam_started_at', 'exam_finished_at',
        'answer_predict_opened_at', 'answer_official_opened_at',
    )
    list_per_page = 20


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(SubmittedAnswer)
class SubmittedAnswerAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(AnswerCount)
class AnswerCountAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(AnswerCountTopRank)
class AnswerCountTopRankAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(AnswerCountMidRank)
class AnswerCountMidRankAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(AnswerCountLowRank)
class AnswerCountLowRankAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(StatisticsVirtual)
class StatisticsVirtualAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_per_page = 20
