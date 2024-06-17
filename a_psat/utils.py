import os
from datetime import datetime

from PIL import Image
from django.db.models import Model

from _config import settings
from a_common.utils import HtmxHttpRequest
from a_psat import models as psat_models, filters

current_year = datetime.now().year


def get_filterset(request: HtmxHttpRequest):
    logged_in = request.user.is_authenticated
    psat_filter = filters.PsatListFilter if logged_in else filters.AnonymousPsatListFilter
    return psat_filter(data=request.GET, request=request)


def get_page_added_path(request: HtmxHttpRequest, page: int):
    curr_path = request.get_full_path()
    if 'page=' not in curr_path:
        curr_path += '&page=1' if '?' in curr_path else '?page=1'
    next_path = curr_path.replace(f'page={page}', f'page={page + 1}')
    return {
        'curr_path': curr_path,
        'next_path': next_path,
    }


def get_elided_page_range(
        request, filterset=None, number=None, num_pages=None,
        *, on_each_side=5, on_ends=1
):
    if filterset is None:
        filterset = get_filterset(request)
    if number is None:
        number = int(request.GET.get('page', 1))
    if num_pages is None:
        num_pages = filterset.qs.count() // 10 + 1
    page_range = range(1, num_pages + 1)

    _ellipsis = "…"
    if num_pages <= (on_each_side + on_ends) * 2:
        yield from page_range
        return

    if number > (1 + on_each_side + on_ends) + 1:
        yield from range(1, on_ends + 1)
        yield _ellipsis
        yield from range(number - on_each_side, number + 1)
    else:
        yield from range(1, number + 1)

    if number < (num_pages - on_each_side - on_ends) - 1:
        yield from range(number + 1, number + on_each_side + 1)
        yield _ellipsis
        yield from range(num_pages - on_ends + 1, num_pages + 1)
    else:
        yield from range(number + 1, num_pages + 1)


def get_problem_images(problem: psat_models.Problem):
    image_folder = os.path.join('image', 'PSAT', str(problem.year))
    filename = f'PSAT{problem.year_ex_sub}{problem.number:02}.png'
    input_image_path = os.path.join(
        settings.STATICFILES_DIRS[0], image_folder, 'input', filename)
    output_image_path = os.path.join(
        settings.STATICFILES_DIRS[0], image_folder, filename)

    if os.path.exists(input_image_path):
        image = Image.open(input_image_path)
        width, height = image.size

        first_image = image.crop((0, 0, width, height // 2))
        second_image = image.crop((0, height // 2, width, height))

        first_image_path = output_image_path.replace('.png', '-1.png')
        second_image_path = output_image_path.replace('.png', '-2.png')

        first_image.save(first_image_path)
        second_image.save(second_image_path)


def get_customized_problems(request, model: Model, **kwargs):
    return model.objects.select_related('problem', 'user').filter(user=request.user, **kwargs)
