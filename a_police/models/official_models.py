import os

from ckeditor.fields import RichTextField
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, TagBase

from _config.settings import BASE_DIR
from a_common.constants import icon_set
from a_common.models import User
from a_police.models.base_settings import (
    get_current_year, year_choice, exam_choices, subject_choices, number_choice
)


class Problem(models.Model):
    year = models.IntegerField(choices=year_choice, default=get_current_year())
    exam = models.CharField(max_length=2, choices=exam_choices, default='경위')
    subject = models.CharField(max_length=2, choices=subject_choices, default='형사')
    number = models.IntegerField(choices=number_choice, default=1)
    answer = models.IntegerField()
    question = models.TextField()
    data = models.TextField()

    tags = TaggableManager(through='ProblemTaggedItem', blank=True)

    open_users = models.ManyToManyField(User, related_name='opened_problems', through='ProblemOpen')
    like_users = models.ManyToManyField(User, related_name='liked_problems', through='ProblemLike')
    rate_users = models.ManyToManyField(User, related_name='rated_problems', through='ProblemRate')
    solve_users = models.ManyToManyField(User, related_name='solved_problems', through='ProblemSolve')
    memo_users = models.ManyToManyField(User, related_name='memoed_problems', through='ProblemMemo')
    comment_users = models.ManyToManyField(
        User, related_name='commented_problems', through='ProblemComment')
    collections = models.ManyToManyField(
        'ProblemCollect', related_name='collected_problems', through='ProblemCollectedItem')

    class Meta:
        verbose_name = "경위공채 기출문제"
        verbose_name_plural = "경위공채 기출문제"
        unique_together = ['year', 'exam', 'subject', 'number']
        ordering = ['-year', 'id']

    def __str__(self):
        return f'[Police]Problem:{self.reference}(id:{self.id})'

    def get_absolute_url(self):
        return reverse('police:problem-detail', args=[self.id])

    # def get_like_url(self):
    #     return reverse('psat:like-problem', args=[self.id])
    #
    # def get_rate_url(self):
    #     return reverse('psat:rate-problem', args=[self.id])
    #
    # def get_solve_url(self):
    #     return reverse('psat:solve-problem', args=[self.id])
    #
    # def get_tag_add_url(self):
    #     return reverse('psat:tag-problem-create', args=[self.id])
    #
    # def get_tag_remove_url(self):
    #     return reverse('psat:tag-problem-remove', args=[self.id])

    @property
    def year_ex_sub(self):
        return f'{self.year}{self.exam}{self.subject}'

    @property
    def reference(self):
        return f'{self.year}{self.subject}{self.number:02}'

    @property
    def full_reference(self):
        return ' '.join([
            self.get_year_display(),
            self.get_exam_display(),
            self.get_subject_display(),
            self.get_number_display(),
        ])

    @property
    def images(self) -> dict:
        def get_image_path_and_name(number):
            filename = f'PSAT{self.year_ex_sub}{self.number:02}-{number}.png'
            image_exists = os.path.exists(
                os.path.join(BASE_DIR, 'static', 'image', 'PSAT', str(self.year), filename))
            path = name = ''
            if number == 1:
                path = static('image/preparing.png')
                name = 'Preparing Image'
            if image_exists:
                path = static(f'image/PSAT/{self.year}/{filename}')
                name = f'Problem Image {number}'
            return path, name

        path1, name1 = get_image_path_and_name(1)
        path2, name2 = get_image_path_and_name(2)
        return {'path1': path1, 'path2': path2, 'name1': name1, 'name2': name2}

    @property
    def department(self):
        for category, subjects in subject_choices():
            for subject in subjects.keys:
                if subject == self.subject:
                    return category.split(' ')[0]

    @property
    def bg_color(self):
        bg_color_dict = {
            '전체': 'bg_heonbeob',
            '일반': 'bg_eoneo',
            '세무회계': 'bg_jaryo',
            '사이버': 'bg_sanghwang',
        }
        return bg_color_dict[self.department]

    @property
    def icon(self):
        return {
            'nav': icon_set.ICON_NAV,
            'like': icon_set.ICON_LIKE,
            'rate': icon_set.ICON_RATE,
            'solve': icon_set.ICON_SOLVE,
            'memo': icon_set.ICON_MEMO,
            'tag': icon_set.ICON_TAG,
            'collection': icon_set.ICON_COLLECTION,
            'question': icon_set.ICON_QUESTION,
        }


class ProblemTag(TagBase):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "경위공채 기출문제 태그"
        verbose_name_plural = "경위공채 기출문제 태그"
        db_table = 'a_police_problem_tag'

    def __str__(self):
        return f'[Police]ProblemTag:{self.name}'


class ProblemTaggedItem(TaggedItemBase):
    created_at = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(ProblemTag, on_delete=models.CASCADE, related_name='tagged_items')
    content_object = models.ForeignKey(
        'Problem', on_delete=models.CASCADE, related_name='tagged_problems')
    user = models.ForeignKey(User, related_name='tagged_police_problems', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    remarks = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "경위공채 기출문제 태그된 문제"
        verbose_name_plural = "경위공채 기출문제 태그된 문제"
        unique_together = ('tag', 'content_object', 'user')
        db_table = 'a_police_problem_tagged_item'


class ProblemOpen(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_problem_open_set')
    ip_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 확인 기록"
        verbose_name_plural = "경위공채 기출문제 확인 기록"
        db_table = 'a_police_problem_open'

    def __str__(self):
        return f'[Police]ProblemOpen:{self.problem.reference}-{self.user.username}'


class ProblemLike(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_problem_like_set')
    is_liked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 즐겨찾기"
        verbose_name_plural = "경위공채 기출문제 즐겨찾기"
        unique_together = ['problem', 'user']
        db_table = 'a_police_problem_like'

    def __str__(self):
        return f'[Police]ProblemLike:{self.problem.reference}-{self.user.username}'


class ProblemRate(models.Model):
    class Ratings(models.IntegerChoices):
        STAR1 = 1, '⭐️'
        STAR2 = 2, '⭐️⭐️'
        STAR3 = 3, '⭐️⭐️⭐️'
        STAR4 = 4, '⭐️⭐️⭐️⭐️'
        STAR5 = 5, '⭐️⭐️⭐️⭐️⭐️'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_problem_rate_set')
    rating = models.IntegerField(choices=Ratings.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 난이도"
        verbose_name_plural = "경위공채 기출문제 난이도"
        unique_together = ['problem', 'user']
        db_table = 'a_police_problem_rate'

    def __str__(self):
        return f'[Police]ProblemRate:{self.problem.reference}-{self.user.username}(rating:{self.rating})'


class ProblemSolve(models.Model):
    class Answers(models.IntegerChoices):
        ANSWER1 = 1, '①'
        ANSWER2 = 2, '②'
        ANSWER3 = 3, '③'
        ANSWER4 = 4, '④'
        ANSWER5 = 5, '⑤'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_problem_solve_set')
    answer = models.IntegerField(choices=Answers.choices)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 정답확인"
        verbose_name_plural = "경위공채 기출문제 정답확인"
        unique_together = ['problem', 'user']
        db_table = 'a_police_problem_solve'

    def __str__(self):
        result = 'O' if self.is_correct else 'X'
        return (f'[Police]ProblemSolve:{self.problem.reference}-{self.user.username}'
                f'(answer:{self.answer},result:{result})')


class ProblemMemo(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_problem_memo_set')
    memo = RichTextField(config_name='minimal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 메모"
        verbose_name_plural = "경위공채 기출문제 메모"
        unique_together = ['problem', 'user']
        db_table = 'a_police_problem_memo'

    def __str__(self):
        return f'[Police]ProblemMemo:{self.problem.reference}-{self.user.username}'


class ProblemComment(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_problem_comment_set')
    title = models.TextField(max_length=100)
    comment = RichTextField(config_name='minimal')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply_comments')
    hit = models.IntegerField(default=1, verbose_name='조회수')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 코멘트"
        verbose_name_plural = "경위공채 기출문제 코멘트"
        unique_together = ['problem', 'user']
        db_table = 'a_police_problem_comment'

    def __str__(self):
        return f'[Police]ProblemComment:{self.problem.reference}-{self.user.username}'


class ProblemCollect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='police_collect_set')
    title = models.CharField(max_length=20)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 컬렉션"
        verbose_name_plural = "경위공채 기출문제 컬렉션"
        unique_together = ["user", "title"]
        db_table = 'a_police_problem_collect'

    def __str__(self):
        return (f'[Police]ProblemCollect:{self.title}-{self.user.username}'
                f'(id:{self.id},user_id:{self.user_id})')


class ProblemCollectedItem(models.Model):
    collect = models.ForeignKey(ProblemCollect, on_delete=models.CASCADE, related_name='collected_items')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='collected_problems')
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "경위공채 기출문제 컬렉션 아이템"
        verbose_name_plural = "경위공채 기출문제 컬렉션 아이템"
        unique_together = ['collect', 'problem']
        db_table = 'a_police_problem_collected_item'

    def __str__(self):
        return (f'[Police]ProblemCollectedItem:{self.problem.reference}'
                f'(collect:{self.collect.title},collect_id:{self.collect_id}')

    def set_active(self):
        self.is_active = True
        self.save()

    def set_inactive(self):
        self.is_active = False
        self.save()
