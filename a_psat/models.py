import os
from datetime import datetime

import pytz
from ckeditor.fields import RichTextField
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, TagBase

from _config.settings import BASE_DIR
from a_common.constants import icon_set
from a_common.models import User

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
    if remarks:
        remarks += f"{separator}{message_type}_at:{utc_now}"
    else:
        remarks = f"{message_type}_at:{utc_now}"
    return remarks


class ProblemTag(TagBase):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'a_psat_problem_tag'


class ProblemTaggedItem(TaggedItemBase):
    created_at = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(
        ProblemTag, on_delete=models.CASCADE, related_name="tagged_psat_problems")
    content_object = models.ForeignKey('Problem', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='tagged_psat_problems', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('tag', 'content_object', 'user')
        db_table = 'a_psat_problem_tagged_item'

    def save(self, *args, **kwargs):
        message_type = kwargs.pop('message_type', 'created')
        self.remarks = get_remarks(message_type, self.remarks)
        super().save(*args, **kwargs)


class Problem(models.Model):
    class ExamChoice(models.TextChoices):
        HAENGSI = '행시', '5급공채/행정고시'
        IPSI = '입시', '입법고시'
        CHILGEUP = '칠급', '7급공채'
        CHILYE = '칠예', '7급공채 예시'
        MINGYUNG = '민경', '민간경력'
        OESI = '외시', '외교원/외무고시'
        GYUNSEUP = '견습', '견습'

    class SubjectChoice(models.TextChoices):
        HEONBEOB = '헌법','헌법'
        EONEO = '언어', '언어논리'
        JARYO = '자료', '자료해석'
        SANGHWANG = '상황', '상황판단'

    year = models.IntegerField(choices=year_choice, default=datetime.now().year)
    exam = models.CharField(max_length=2, choices=ExamChoice, default=ExamChoice.HAENGSI)
    subject = models.CharField(max_length=2, choices=SubjectChoice, default=SubjectChoice.EONEO)
    number = models.IntegerField(choices=number_choice, default=1)
    answer = models.IntegerField()
    question = models.TextField()
    data = models.TextField()

    tags = TaggableManager(through=ProblemTaggedItem, blank=True)

    open_users = models.ManyToManyField(User, related_name='opened_psat_problems', through='ProblemOpen')
    like_users = models.ManyToManyField(User, related_name='liked_psat_problems', through='ProblemLike')
    rate_users = models.ManyToManyField(User, related_name='rated_psat_problems', through='ProblemRate')
    solve_users = models.ManyToManyField(User, related_name='solved_psat_problems', through='ProblemSolve')
    memo_users = models.ManyToManyField(User, related_name='memoed_psat_problems', through='ProblemMemo')
    comment_users = models.ManyToManyField(User, related_name='commented_psat_problems', through='ProblemComment')
    collections = models.ManyToManyField(
        'ProblemCollection', related_name='collected_psat_problems', through='ProblemCollectionItem')

    class Meta:
        ordering = ['-year', 'id']

    def __str__(self):
        return f'{self.year_ex_sub}-{self.number}({self.id})'

    @property
    def year_ex_sub(self):
        return f'{self.year}{self.exam}{self.subject}'

    @property
    def year_exam_subject(self):
        return ' '.join([self.get_year_display(), self.exam_name, self.get_subject_display()])

    @property
    def exam_name(self):
        if self.exam == '행시':
            return '행정고시' if self.year < 2011 else '5급공채'
        if self.exam == '외시':
            return '외교원' if self.year == 2013 else '외무고시'
        if self.exam == '칠급':
            return '7급공채 모의고사' if self.year == 2020 else '7급공채'
        if self.exam == '칠예':
            return '7급공채 예시'
        return self.get_exam_display()

    @property
    def full_reference(self):
        return ' '.join([self.year_exam_subject, self.get_number_display()])

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
    def bg_color(self):
        bg_color_dict = {
            '헌법': 'bg_heonbeob',
            '언어': 'bg_eoneo',
            '자료': 'bg_jaryo',
            '상황': 'bg_sanghwang',
        }
        return bg_color_dict[self.subject]

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

    def get_absolute_url(self):
        return reverse('psat:problem-detail', args=[self.id])

    def get_like_url(self):
        return reverse('psat:like-problem', args=[self.id])

    def get_rate_url(self):
        return reverse('psat:rate-problem', args=[self.id])

    def get_solve_url(self):
        return reverse('psat:solve-problem', args=[self.id])

    def get_tag_create_url(self):
        return reverse('psat:tag-problem-create', args=[self.id])

    def get_tag_remove_url(self):
        return reverse('psat:tag-problem-remove', args=[self.id])

    def get_comment_create_url(self):
        return reverse('psat:comment-problem-create', args=[self.id])


class ProblemOpen(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.problem} Open by {self.user.username}'

    class Meta:
        db_table = 'a_psat_problem_open'


class ProblemLike(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.is_liked:
            return f'{self.problem} Liked by {self.user.username}'
        return f'{self.problem} Unliked by {self.user.username}'

    class Meta:
        unique_together = ['user', 'problem']
        ordering = ['-id']
        db_table = 'a_psat_problem_like'

    def save(self, *args, **kwargs):
        message_type = kwargs.pop('message_type', 'liked')
        self.remarks = get_remarks(message_type, self.remarks)
        super().save(*args, **kwargs)


class ProblemRate(models.Model):
    class Ratings(models.IntegerChoices):
        STAR1 = 1, '⭐️'
        STAR2 = 2, '⭐️⭐️'
        STAR3 = 3, '⭐️⭐️⭐️'
        STAR4 = 4, '⭐️⭐️⭐️⭐️'
        STAR5 = 5, '⭐️⭐️⭐️⭐️⭐️'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=Ratings.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.problem} Rated({self.rating}) by {self.user.username}'

    class Meta:
        unique_together = ['user', 'problem']
        ordering = ['-id']
        db_table = 'a_psat_problem_rate'

    def save(self, *args, **kwargs):
        message_type = kwargs.pop('message_type', 'rated')
        message_type = f'{message_type}({self.rating})'
        self.remarks = get_remarks(message_type, self.remarks)
        super().save(*args, **kwargs)


class ProblemSolve(models.Model):
    class Answers(models.IntegerChoices):
        ANSWER1 = 1, '①'
        ANSWER2 = 2, '②'
        ANSWER3 = 3, '③'
        ANSWER4 = 4, '④'
        ANSWER5 = 5, '⑤'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.IntegerField(choices=Answers.choices)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.is_correct:
            return f'{self.problem} Correct({self.answer}) by {self.user.username}'
        return f'{self.problem} Wrong({self.answer}) by {self.user.username}'

    class Meta:
        unique_together = ['user', 'problem']
        ordering = ['-id']
        db_table = 'a_psat_problem_solve'

    def save(self, *args, **kwargs):
        message_type = 'correct' if self.is_correct else 'wrong'
        message_type = f'{message_type}({self.answer})'
        self.remarks = get_remarks(message_type, self.remarks)
        super().save(*args, **kwargs)


class ProblemMemo(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField(config_name='minimal')
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:30]} [{self.problem}-Memo]'

    class Meta:
        unique_together = ['user', 'problem']
        ordering = ['-id']
        db_table = 'a_psat_problem_memo'


class ProblemComment(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    like_users = models.ManyToManyField(
        User, related_name='liked_psat_problem_comments', through='ProblemCommentLike')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply_comments')
    hit = models.IntegerField(default=1, verbose_name='조회수')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        prefix = '↪ ' if self.parent else ''
        return f'{prefix}{self.user.username}: {self.content[:30]} [{self.problem}-Comment]'

    class Meta:
        ordering = ['-id']
        db_table = 'a_psat_problem_comment'


class ProblemCommentLike(models.Model):
    comment = models.ForeignKey(ProblemComment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.comment.content[:30]}'

    class Meta:
        db_table = 'a_psat_problem_comment_like'

    def save(self, *args, **kwargs):
        message_type = kwargs.pop('message_type', 'liked')
        self.remarks = get_remarks(message_type, self.remarks)
        super().save(*args, **kwargs)


class ProblemCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "title"]]
        ordering = ['-id']
        db_table = 'a_psat_problem_collection'

    def __str__(self):
        title = f'[User{self.user_id}_Col{self.id}] {self.title}'
        return title


class ProblemCollectionItem(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    collection = models.ForeignKey(ProblemCollection, on_delete=models.CASCADE, related_name='collection_items')
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['collection__user', 'collection', 'order']
        db_table = 'a_psat_problem_collection_item'

    def __str__(self):
        return f'{self.collection} - {self.problem}'

    def set_active(self):
        self.is_active = True
        self.save()

    def set_inactive(self):
        self.is_active = False
        self.save()
