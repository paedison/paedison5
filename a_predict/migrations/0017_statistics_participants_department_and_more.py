# Generated by Django 5.0.6 on 2024-06-23 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_predict', '0016_studentanswer_answer_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='participants_department',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statistics',
            name='participants_total',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statistics',
            name='rank_department',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statistics',
            name='rank_total',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statistics',
            name='score',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statisticsvirtual',
            name='participants_department',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statisticsvirtual',
            name='participants_total',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statisticsvirtual',
            name='rank_department',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statisticsvirtual',
            name='rank_total',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='statisticsvirtual',
            name='score',
            field=models.JSONField(default=dict),
        ),
    ]