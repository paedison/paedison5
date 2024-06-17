from bs4 import BeautifulSoup as bs

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from a_common import utils as common_utils
from a_common.constants import icon_set
from a_psat import models as psat_models, utils as psat_utils
from a_psat import forms as psat_forms


def get_list_variables(request: common_utils.HtmxHttpRequest):
    filterset = psat_utils.get_filterset(request)
    paginator = Paginator(filterset.qs, per_page=10)
    page = int(request.GET.get('page', 1))
    elided_page_range = psat_utils.get_elided_page_range(
        request, filterset, page, paginator.num_pages)
    return filterset, paginator, page, elided_page_range


def problem_list_view(request: common_utils.HtmxHttpRequest, tag=None):
    filterset, paginator, page, elided_page_range = get_list_variables(request)

    info = {'menu': 'psat'}
    next_path = psat_utils.get_page_added_path(request, page)['next_path']

    try:
        problems = paginator.page(page)
    except EmptyPage:
        return HttpResponse('')

    context = common_utils.update_context_data(
        info=info,
        problems=problems,
        tag=tag,
        form=filterset.form,
        next_path=next_path,
        page=page,
        elided_page_range=elided_page_range,
        show_first_page=True,
        show_next_page=False,
    )
    if request.htmx:
        if request.headers.get('Open-First-Page') != 'true':
            context = common_utils.update_context_data(
                context, show_first_page=False, show_next_page=True)
        return render(request, 'a_psat/problem_list_content.html', context)
    return render(request, 'a_psat/problem_list.html', context)


def problem_list_filter(request: common_utils.HtmxHttpRequest):
    filterset, paginator, page, elided_page_range = get_list_variables(request)
    context = {
        'form': filterset.form,
        'page': page,
        'elided_page_range': elided_page_range,
    }
    return render(request, 'a_psat/snippets/filter_list.html', context)


def problem_detail_view(request: common_utils.HtmxHttpRequest, pk: int | None = None):
    if pk is None:
        pk_list = request.GET.getlist('pk')
        for p in pk_list:
            if str(p).isdigit():
                return redirect('psat:problem-detail', p)

    queryset = psat_models.Problem.objects
    problem = get_object_or_404(queryset, pk=pk)
    psat_utils.get_problem_images(problem)

    problem_neighbors = queryset.filter(year=problem.year, exam=problem.exam, subject=problem.subject)
    problem_likes = problem_rates = problem_solves = problem_comments = None
    if request.user.is_authenticated:
        problem_likes = psat_utils.get_customized_problems(request, psat_models.ProblemLike)
        problem_rates = psat_utils.get_customized_problems(request, psat_models.ProblemRate)
        problem_solves = psat_utils.get_customized_problems(request, psat_models.ProblemSolve)
        problem_comments = psat_utils.get_customized_problems(
            request, psat_models.ProblemComment, parent__isnull=True)

    comment_form = psat_forms.ProblemCommentForm()
    reply_form = psat_forms.ProblemCommentForm()
    info = {'menu': 'psat'}
    context = common_utils.update_context_data(
        info=info,
        problem=problem,
        problem_neighbors=problem_neighbors,
        problem_likes=problem_likes,
        problem_rates=problem_rates,
        problem_solves=problem_solves,
        problem_comments=problem_comments,
        comment_form=comment_form,
        reply_form=reply_form,
    )
    if request.htmx:
        return render(request, 'a_psat/problem_detail_content.html', context)
    return render(request, 'a_psat/problem_detail.html', context)


def get_problem(pk: int):
    return get_object_or_404(psat_models.Problem, pk=pk)


@login_required
def like_problem(request: common_utils.HtmxHttpRequest, pk: int):
    problem = get_problem(pk)

    if request.method == 'POST':
        problem_like, created = psat_models.ProblemLike.objects.get_or_create(
            problem=problem, user=request.user,
        )

        is_liked = True
        if not created:
            is_liked = not problem_like.is_liked
            problem_like.is_liked = is_liked
            message_type = 'liked' if is_liked else 'unliked'
            problem_like.save(message_type=message_type)

        icon_like = icon_set.ICON_LIKE[f'{is_liked}']
        like_users = psat_models.ProblemLike.objects.filter(
            problem=problem, is_liked=True).count()
        return HttpResponse(f'{icon_like} {like_users}')


@login_required
def rate_problem(request: common_utils.HtmxHttpRequest, pk: int):
    problem = get_problem(pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        problem_rate = psat_models.ProblemRate.objects.filter(problem=problem, user=request.user)
        if problem_rate:
            problem_rate = problem_rate.first()
            problem_rate.rating = rating
            problem_rate.save(message_type='rerated')
        else:
            psat_models.ProblemRate.objects.create(
                problem=problem, user=request.user, rating=rating)
        icon_rate = icon_set.ICON_RATE[f'star{rating}']
        return HttpResponse(icon_rate)

    context = {
        'problem': problem,
    }
    return render(request, 'a_psat/snippets/rate_modal.html', context)


@login_required
def solve_problem(request: common_utils.HtmxHttpRequest, pk: int):
    problem = get_problem(pk)

    if request.method == 'POST':
        answer = int(request.POST.get('answer'))
        is_correct = answer == problem.answer
        problem_solve = psat_models.ProblemSolve.objects.filter(problem=problem, user=request.user)
        if problem_solve:
            problem_solve = problem_solve.first()
            problem_solve.answer = answer
            problem_solve.is_correct = is_correct
            problem_solve.save()
        else:
            psat_models.ProblemSolve.objects.create(
                problem=problem, user=request.user, answer=answer, is_correct=is_correct)
        context = {
            'problem': problem,
            'icon_solve': icon_set.ICON_SOLVE[f'{is_correct}'],
            'is_correct': is_correct,
        }
        return render(request, 'a_psat/snippets/solve_result.html', context)

    context = {
        'problem': problem,
    }
    return render(request, 'a_psat/snippets/solve_modal.html', context)


@login_required
def tag_problem_create(request: common_utils.HtmxHttpRequest, pk: int):
    problem = get_problem(pk)

    if request.method == 'POST':
        name = request.POST.get('tag')
        tag, created = psat_models.ProblemTag.objects.get_or_create(name=name)
        tagged_problem, created = psat_models.ProblemTaggedItem.objects.get_or_create(
            tag=tag, content_object=problem, user=request.user)
        if not created:
            tagged_problem.active = True
            tagged_problem.save(message_type='recreated')

        return HttpResponse('')


@login_required
def tag_problem_remove(request: common_utils.HtmxHttpRequest, pk: int):
    problem = get_problem(pk)

    if request.method == 'POST':
        tagged_problem = get_object_or_404(
            psat_models.ProblemTaggedItem,
            tag__name=request.POST.get('tag'),
            content_object=problem, user=request.user,
        )
        tagged_problem.active = False
        tagged_problem.save(message_type='removed')
        return HttpResponse('')


@login_required
def comment_problem_create(request: common_utils.HtmxHttpRequest, pk: int):
    problem = get_problem(pk)
    reply_form = psat_forms.ProblemCommentForm()

    if request.method == 'POST':
        form = psat_forms.ProblemCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)

            content = form.cleaned_data['content']
            soup = bs(content, 'html.parser')
            title = soup.get_text()[:20]

            comment.problem = problem
            comment.user = request.user
            comment.title = title
            comment.save()
            context = {
                'comment': comment,
                'problem': problem,
                'reply_form': reply_form,
            }
            # return HttpResponse('')
            return render(request, 'a_psat/snippets/comment.html', context)


@login_required
def comment_problem_update(request: common_utils.HtmxHttpRequest, pk: int):
    comment = get_object_or_404(ProblemComment, pk=pk)
    if request.method == 'POST':
        form = ProblemCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('problemcomment-list')
    else:
        form = ProblemCommentForm(instance=comment)
    return render(request, 'problemcomment_form.html', {'form': form})


@login_required
def comment_problem_delete(request: common_utils.HtmxHttpRequest, pk: int):
    comment = get_object_or_404(ProblemComment, pk=pk)
    if request.method == 'POST':
        comment.delete()
        return redirect('problemcomment-list')
    return render(request, 'problemcomment_confirm_delete.html', {'comment': comment})