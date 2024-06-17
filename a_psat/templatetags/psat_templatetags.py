from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.template import Library, Node

from a_common.constants import icon_set
from a_common import utils as common_utils
from a_psat import models as psat_models

register = Library()


@register.inclusion_tag('a_psat/templatetags/psat_icons.html')
def psat_icons(user: User, problem: psat_models.Problem):
    problem_likes = psat_models.ProblemLike.objects.filter(
        problem=problem, is_liked=True
    )
    like_exists = False
    if user.is_authenticated:
        like_exists = problem_likes.filter(user=user).exists()
    icon_like = icon_set.ICON_LIKE[f'{like_exists}']
    like_counts = problem_likes.count()

    rating = 0
    if user in problem.rate_users.all():
        rating = problem.problemrate_set.filter(user=user).first().rating
    icon_rate = icon_set.ICON_RATE[f'star{rating}']

    is_correct = None
    if user in problem.solve_users.all():
        is_correct = problem.problemsolve_set.filter(user=user).first().is_correct
    icon_solve = icon_set.ICON_SOLVE[f'{is_correct}']

    is_memoed = False
    if user in problem.memo_users.all():
        is_memoed = problem.problemsolve_set.filter(user=user).first().is_correct
    icon_memo = icon_set.ICON_MEMO[f'{is_memoed}']

    context = common_utils.update_context_data(
        user=user,
        problem=problem,
        icon_like=icon_like,
        like_counts=like_counts,
        icon_rate=icon_rate,
        icon_solve=icon_solve,
        icon_memo=icon_memo,
    )
    return context


@register.inclusion_tag('a_psat/templatetags/tags.html')
def psat_tag(user: User, problem: psat_models.Problem):
    tags = []
    tagged_problem = None
    if user.is_authenticated:
        tagged_problem = psat_models.ProblemTaggedItem.objects.filter(
            user=user, content_object=problem,
        )
    if tagged_problem:
        tags = psat_models.ProblemTag.objects.filter(
            tagged_psat_problems__content_object=problem,
            tagged_psat_problems__user=user,
            tagged_psat_problems__active=True,
        ).values_list('name', flat=True)
    return {
        'user': user,
        'problem': problem,
        'tags': tags,
    }


@register.filter
def subtract(value, arg) -> int:  # Subtract arg from value
    return arg - int(value)
