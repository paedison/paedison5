import os
from datetime import datetime

import pytz
from ckeditor.fields import RichTextField
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from taggit.managers import TaggableManager

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


class Problem(models.Model):
    # class YearChoice(models.IntegerChoices):
    #     current_year = datetime.now().year
    #     choices = [(year, f'{year}년') for year in range(2023, current_year + 1)]
    #     for year, label in choices:
    #         vars()[f'YEAR{year}'] = year
        # for year in range(2023, current_year + 1):
        #     vars()[f'YEAR{year}'] = year, f'{year}년'

    class ExamChoice(models.TextChoices):
        SUB_INSPECTOR = '경위', '경위공채'

    class SubjectChoice(models.TextChoices):
        HYEONGSA = '형사','형사법'
        HEONBEOB = '헌법','헌법'
        GYEONGCHAL = '경찰','경찰학'
        BEOMJOE = '범죄','범죄학'
        HAENGBEOB = '행법','행정법'
        HAENGHAG = '행학','행정학'
        MINBEOB = '민법','민법총칙'
        SEBEOB = '세법','세법개론'
        HOEGYE = '회계','회계학'
        SANGBEOB = '상법','상법총칙'
        GYEONGJE = '경제','경제학'
        TONGGYE = '통계','통계학'
        JAEJEONG = '재정','재정학'
        JEONGBO = '정보','정보보호론'
        SINE = '시네','시스템네트워크보안'
        DEBE = '데베','데이터베이스론'
        TONGSIN = '통신','통신이론'
        SOWE = '소웨','소프트웨어공학'

    class DepartmentChoice(models.TextChoices):
        ALL = '전체', '전체'
        GENERAL = '일반', '일반'
        TAX = '세무회계', '세무회계'
        CYBER = '사이버', '사이버'

    class CategoryChoice(models.TextChoices):
        COMMON = '공통', '공통'
        ESSENTIAL = '필수', '필수'
        SELECT = '선택', '선택'

    # class NumberChoice(models.IntegerChoices):
    #     for number in range(1, 41):
    #         vars()[f'NUMBER{number}'] = number, f'{number}번'

    year = models.IntegerField(choices=year_choice, default=current_year)
    exam = models.CharField(max_length=2, choices=ExamChoice, default=ExamChoice.SUB_INSPECTOR)
    subject = models.CharField(max_length=2, choices=SubjectChoice, default=SubjectChoice.HYEONGSA)
    department = models.CharField(max_length=5, choices=DepartmentChoice, default=DepartmentChoice.ALL)
    category = models.CharField(max_length=5, choices=CategoryChoice, default=CategoryChoice.COMMON)
    number = models.IntegerField(choices=number_choice, default=1)
    answer = models.IntegerField()
    question = models.TextField()
    data = models.TextField()

    # open_users = models.ManyToManyField(User, related_name='opened_problems', through='ProblemOpen')
    # like_users = models.ManyToManyField(User, related_name='liked_problems', through='ProblemLike')
    # rate_users = models.ManyToManyField(User, related_name='rated_problems', through='ProblemRate')
    # solve_users = models.ManyToManyField(User, related_name='solved_problems', through='ProblemSolve')
    # memo_users = models.ManyToManyField(User, related_name='memoed_problems', through='ProblemMemo')
    # tag_users = models.ManyToManyField(User, related_name='tagged_problems', through='ProblemTag')
    # comment_users = models.ManyToManyField(User, related_name='commented_problems', through='ProblemComment')
    # collection_users = models.ManyToManyField('Collection', related_name='collected_problems', through='ProblemCollection')

    class Meta:
        ordering = ['-year', 'id']

    def __str__(self):
        return f'{self.year_ex_sub}-{self.number}({self.id})'

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
    def bg_color(self):
        bg_color_dict = {
            '전체': 'bg_heonbeob',
            '일반': 'bg_eoneo',
            '세무회계': 'bg_jaryo',
            '사이버': 'bg_sanghwang',
        }
        return bg_color_dict[self.department]

    # @property
    # def icon(self):
    #     return {
    #         'nav': icon_set.ICON_NAV,
    #         'like': icon_set.ICON_LIKE,
    #         'rate': icon_set.ICON_RATE,
    #         'solve': icon_set.ICON_SOLVE,
    #         'memo': icon_set.ICON_MEMO,
    #         'tag': icon_set.ICON_TAG,
    #         'collection': icon_set.ICON_COLLECTION,
    #         'question': icon_set.ICON_QUESTION,
    #     }


# class ProblemOpen(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     ip_address = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f'{self.problem} Open by {self.user.username}'
#
#
# class ProblemLike(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     is_liked = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f'{self.problem} Like by {self.user.username}'
#
#     class Meta:
#         ordering = ['user', 'problem']
#
#
# class ProblemRate(models.Model):
#     class Ratings(models.IntegerChoices):
#         STAR1 = 1, '⭐️'
#         STAR2 = 2, '⭐️⭐️'
#         STAR3 = 3, '⭐️⭐️⭐️'
#         STAR4 = 4, '⭐️⭐️⭐️⭐️'
#         STAR5 = 5, '⭐️⭐️⭐️⭐️⭐️'
#
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     rating = models.IntegerField(choices=Ratings.choices)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f'{self.problem} Rate({self.rating}) by {self.user.username}'
#
#     class Meta:
#         ordering = ['user', 'problem']
#
#
# class ProblemSolve(models.Model):
#     class Answers(models.IntegerChoices):
#         ANSWER1 = 1, '①'
#         ANSWER2 = 2, '②'
#         ANSWER3 = 3, '③'
#         ANSWER4 = 4, '④'
#         ANSWER5 = 5, '⑤'
#
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     answer = models.IntegerField(choices=Answers.choices)
#     is_correct = models.BooleanField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         result = 'O' if self.is_correct else 'X'
#         return f'{self.problem} Solve({result}, {self.answer}) by {self.user.username}'
#
#     class Meta:
#         ordering = ['user', 'problem']
#
#
# class ProblemMemo(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     memo = RichTextField(config_name='minimal')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f'{self.problem} Memo by {self.user.username}'
#
#     class Meta:
#         ordering = ['user', 'problem']
#
#
# class ProblemTag(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     tags = TaggableManager()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f'{self.problem} Tag by {self.user.username}'
#
#     class Meta:
#         ordering = ['user', 'problem']
#
#
# class ProblemComment(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.TextField(max_length=100)
#     comment = RichTextField(config_name='minimal')
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply_comments')
#     hit = models.IntegerField(default=1, verbose_name='조회수')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f'{self.problem} Comment by {self.user.username}'
#
#     class Meta:
#         ordering = ['user', 'problem']
#
#
# class Collection(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=20)
#     order = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['user', 'order']
#         unique_together = [["user", "title"]]
#
#     def __str__(self):
#         title = f'[User{self.user_id}_Col{self.id}] {self.title}'
#         return title
#
#
# class ProblemCollection(models.Model):
#     problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#     collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_items')
#     order = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['collection__user', 'collection', 'order']
#
#     def __str__(self):
#         return f'{self.collection} - {self.problem}'
#
#     def set_active(self):
#         self.is_active = True
#         self.save()
#
#     def set_inactive(self):
#         self.is_active = False
#         self.save()
