# Generated by Django 5.0.6 on 2024-06-20 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_predict', '0010_studentanswer_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswer',
            name='eoneo_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentanswer',
            name='heonbeob_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentanswer',
            name='jaryo_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentanswer',
            name='sanghwang_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]