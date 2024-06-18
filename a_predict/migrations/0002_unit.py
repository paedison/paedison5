# Generated by Django 5.0.6 on 2024-06-18 07:39

import a_predict.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_predict', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('exam', models.CharField(choices=[('행시', '5급공채/행정고시'), ('입시', '입법고시'), ('칠급', '7급공채'), ('프모', '프라임모의고사')], max_length=2)),
                ('unit', models.CharField(max_length=128)),
                ('order', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, a_predict.models.ChoiceMethod),
        ),
    ]
