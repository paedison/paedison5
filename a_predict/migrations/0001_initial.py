# Generated by Django 5.0.6 on 2024-06-17 10:33

import a_predict.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('year', models.IntegerField(choices=a_predict.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('round', models.IntegerField(default=0)),
                ('subject', models.CharField(choices=[('헌법', '헌법'), ('언어', '언어논리'), ('자료', '자료해석'), ('상황', '상황판단')], max_length=2)),
                ('number', models.IntegerField()),
                ('answer', models.IntegerField(blank=True, null=True)),
                ('count_1', models.IntegerField(default=0)),
                ('count_2', models.IntegerField(default=0)),
                ('count_3', models.IntegerField(default=0)),
                ('count_4', models.IntegerField(default=0)),
                ('count_5', models.IntegerField(default=0)),
                ('count_0', models.IntegerField(default=0)),
                ('count_None', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '성적 예측 답안 개수(전체)',
                'verbose_name_plural': '성적 예측 답안 개수(전체)',
                'db_table': 'a_predict_answer_count',
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='AnswerCountLowRank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('year', models.IntegerField(choices=a_predict.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('round', models.IntegerField(default=0)),
                ('subject', models.CharField(choices=[('헌법', '헌법'), ('언어', '언어논리'), ('자료', '자료해석'), ('상황', '상황판단')], max_length=2)),
                ('number', models.IntegerField()),
                ('answer', models.IntegerField(blank=True, null=True)),
                ('count_1', models.IntegerField(default=0)),
                ('count_2', models.IntegerField(default=0)),
                ('count_3', models.IntegerField(default=0)),
                ('count_4', models.IntegerField(default=0)),
                ('count_5', models.IntegerField(default=0)),
                ('count_0', models.IntegerField(default=0)),
                ('count_None', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '성적 예측 답안 개수(하위권)',
                'verbose_name_plural': '성적 예측 답안 개수(하위권)',
                'db_table': 'a_predict_answer_count_low_rank',
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='AnswerCountMidRank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('year', models.IntegerField(choices=a_predict.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('round', models.IntegerField(default=0)),
                ('subject', models.CharField(choices=[('헌법', '헌법'), ('언어', '언어논리'), ('자료', '자료해석'), ('상황', '상황판단')], max_length=2)),
                ('number', models.IntegerField()),
                ('answer', models.IntegerField(blank=True, null=True)),
                ('count_1', models.IntegerField(default=0)),
                ('count_2', models.IntegerField(default=0)),
                ('count_3', models.IntegerField(default=0)),
                ('count_4', models.IntegerField(default=0)),
                ('count_5', models.IntegerField(default=0)),
                ('count_0', models.IntegerField(default=0)),
                ('count_None', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '성적 예측 답안 개수(중위권)',
                'verbose_name_plural': '성적 예측 답안 개수(중위권)',
                'db_table': 'a_predict_answer_count_mid_rank',
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='AnswerCountTopRank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('year', models.IntegerField(choices=a_predict.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('round', models.IntegerField(default=0)),
                ('subject', models.CharField(choices=[('헌법', '헌법'), ('언어', '언어논리'), ('자료', '자료해석'), ('상황', '상황판단')], max_length=2)),
                ('number', models.IntegerField()),
                ('answer', models.IntegerField(blank=True, null=True)),
                ('count_1', models.IntegerField(default=0)),
                ('count_2', models.IntegerField(default=0)),
                ('count_3', models.IntegerField(default=0)),
                ('count_4', models.IntegerField(default=0)),
                ('count_5', models.IntegerField(default=0)),
                ('count_0', models.IntegerField(default=0)),
                ('count_None', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '성적 예측 답안 개수(상위권)',
                'verbose_name_plural': '성적 예측 답안 개수(상위권)',
                'db_table': 'a_predict_answer_count_top_rank',
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('unit', models.CharField(max_length=128)),
                ('department', models.CharField(max_length=128)),
                ('order', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('page_opened_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('exam_started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('exam_finished_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('answer_predict_opened_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('answer_official_opened_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('year', models.IntegerField(choices=a_predict.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('unit', models.CharField(max_length=128)),
                ('department', models.CharField(max_length=128)),
                ('serial_start', models.IntegerField()),
                ('serial_end', models.IntegerField()),
                ('region', models.CharField(max_length=10)),
                ('school', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=50)),
                ('contact', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('year', models.IntegerField(choices=a_predict.models.year_choice, default=2024)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('round', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=20)),
                ('serial', models.CharField(max_length=10)),
                ('unit', models.CharField(max_length=128)),
                ('department', models.CharField(max_length=128)),
                ('password', models.IntegerField()),
                ('prime_id', models.CharField(blank=True, max_length=15, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='psat_predict_students', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '성적 예측 수험 정보',
                'verbose_name_plural': '성적 예측 수험 정보',
                'unique_together': {('year', 'exam', 'round', 'user')},
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='StatisticsVirtual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('score_heonbeob', models.FloatField(blank=True, null=True)),
                ('score_eoneo', models.FloatField(blank=True, null=True)),
                ('score_jaryo', models.FloatField(blank=True, null=True)),
                ('score_sanghwang', models.FloatField(blank=True, null=True)),
                ('rank_total_heonbeob', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_eoneo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_jaryo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_sanghwang', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_psat', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_heonbeob', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_eoneo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_jaryo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_sanghwang', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_psat', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_ratio_total_heonbeob', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_eoneo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_jaryo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_sanghwang', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_psat', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_heonbeob', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_eoneo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_jaryo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_sanghwang', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_psat', models.FloatField(blank=True, null=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statistics_virtual', to='a_predict.student')),
            ],
            options={
                'db_table': 'a_predict_statistics_virtual',
            },
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('score_heonbeob', models.FloatField(blank=True, null=True)),
                ('score_eoneo', models.FloatField(blank=True, null=True)),
                ('score_jaryo', models.FloatField(blank=True, null=True)),
                ('score_sanghwang', models.FloatField(blank=True, null=True)),
                ('rank_total_heonbeob', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_eoneo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_jaryo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_sanghwang', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_total_psat', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_heonbeob', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_eoneo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_jaryo', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_sanghwang', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_department_psat', models.PositiveIntegerField(blank=True, null=True)),
                ('rank_ratio_total_heonbeob', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_eoneo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_jaryo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_sanghwang', models.FloatField(blank=True, null=True)),
                ('rank_ratio_total_psat', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_heonbeob', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_eoneo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_jaryo', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_sanghwang', models.FloatField(blank=True, null=True)),
                ('rank_ratio_department_psat', models.FloatField(blank=True, null=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='a_predict.student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('answer_heonbeob', models.TextField()),
                ('answer_eoneo', models.TextField()),
                ('answer_jaryo', models.TextField()),
                ('answer_sanghwang', models.TextField()),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='a_predict.student')),
            ],
            options={
                'verbose_name': '성적 예측 제출 답안',
                'verbose_name_plural': '성적 예측 제출 답안',
                'db_table': 'a_predict_student_answer',
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
        migrations.CreateModel(
            name='SubmittedAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('subject', models.CharField(choices=[('헌법', '헌법'), ('언어', '언어논리'), ('자료', '자료해석'), ('상황', '상황판단')], max_length=2)),
                ('number', models.IntegerField(choices=a_predict.models.number_choice, default=1)),
                ('answer', models.IntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_answers', to='a_predict.student')),
            ],
            options={
                'db_table': 'a_predict_submitted_answer',
                'unique_together': {('student', 'subject', 'number')},
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
    ]
