from django.contrib import admin

from . import models


@admin.register(models.Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = list_display_links = ['id', 'year', 'exam', 'subject', 'number', 'answer', 'question']
    list_filter = ['year', 'exam', 'subject']
    show_facets = admin.ShowFacets.ALWAYS
    save_on_top = True
    search_fields = ['data']
    show_full_result_count = True
