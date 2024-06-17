# Generated by Django 5.0.6 on 2024-06-17 05:31

import a_psat.models
import ckeditor.fields
import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(choices=a_psat.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('칠예', '7급공채 예시'), ('민경', '민간경력'), ('외시', '외교원/외무고시'), ('견습', '견습')], default='행시', max_length=2)),
                ('subject', models.CharField(choices=[('헌법', '헌법'), ('언어', '언어논리'), ('자료', '자료해석'), ('상황', '상황판단')], default='언어', max_length=2)),
                ('number', models.IntegerField(choices=a_psat.models.number_choice, default=1)),
                ('answer', models.IntegerField()),
                ('question', models.TextField()),
                ('data', models.TextField()),
            ],
            options={
                'ordering': ['-year', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ProblemTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='slug')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProblemCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('order', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'unique_together': {('user', 'title')},
            },
        ),
        migrations.CreateModel(
            name='ProblemCollectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_items', to='a_psat.problemcollection')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
            ],
            options={
                'ordering': ['collection__user', 'collection', 'order'],
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='collections',
            field=models.ManyToManyField(related_name='collected_psat_problems', through='a_psat.ProblemCollectionItem', to='a_psat.problemcollection'),
        ),
        migrations.CreateModel(
            name='ProblemComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('hit', models.IntegerField(default=1, verbose_name='조회수')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_comments', to='a_psat.problemcomment')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='comment_users',
            field=models.ManyToManyField(related_name='commented_psat_problems', through='a_psat.ProblemComment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemCommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_liked', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problemcomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='problemcomment',
            name='like_users',
            field=models.ManyToManyField(related_name='liked_psat_problem_comments', through='a_psat.ProblemCommentLike', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_liked', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'unique_together': {('user', 'problem')},
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='like_users',
            field=models.ManyToManyField(related_name='liked_psat_problems', through='a_psat.ProblemLike', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemMemo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', ckeditor.fields.RichTextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'unique_together': {('user', 'problem')},
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='memo_users',
            field=models.ManyToManyField(related_name='memoed_psat_problems', through='a_psat.ProblemMemo', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemOpen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='open_users',
            field=models.ManyToManyField(related_name='opened_psat_problems', through='a_psat.ProblemOpen', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '⭐️'), (2, '⭐️⭐️'), (3, '⭐️⭐️⭐️'), (4, '⭐️⭐️⭐️⭐️'), (5, '⭐️⭐️⭐️⭐️⭐️')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'unique_together': {('user', 'problem')},
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='rate_users',
            field=models.ManyToManyField(related_name='rated_psat_problems', through='a_psat.ProblemRate', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemSolve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.IntegerField(choices=[(1, '①'), (2, '②'), (3, '③'), (4, '④'), (5, '⑤')])),
                ('is_correct', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'unique_together': {('user', 'problem')},
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='solve_users',
            field=models.ManyToManyField(related_name='solved_psat_problems', through='a_psat.ProblemSolve', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ProblemTaggedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('content_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a_psat.problem')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_psat_problems', to='a_psat.problemtag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_psat_problems', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('tag', 'content_object', 'user')},
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='a_psat.ProblemTaggedItem', to='a_psat.ProblemTag', verbose_name='Tags'),
        ),
    ]
