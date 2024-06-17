from django.urls import path, include

from .views import *

app_name = 'police'

problem_patterns = [
    path('', problem_detail_view, name='problem-detail-base'),
    path('<int:pk>/', problem_detail_view, name='problem-detail'),
    # path('like/<int:pk>/', like_problem, name='like-problem'),
    # path('rate/<int:pk>/', rate_problem, name='rate-problem'),
    # path('solve/<int:pk>/', solve_problem, name='solve-problem'),
    # path('tag/add/<int:pk>/', tag_problem_add, name='tag-problem-create'),
    # path('tag/remove/<int:pk>/', tag_problem_remove, name='tag-problem-remove'),
]

urlpatterns = [
    path('', problem_list_view, name='problem-list'),
    path('filter/list/', problem_list_filter, name='problem-list-filter'),
    path('category/<tag>/', problem_list_view, name='category'),

    path('problem/', include(problem_patterns)),
]
