# Generated by Django 5.0.6 on 2024-06-17 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('a_psat', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='problemcollection',
            table='a_psat_problem_collection',
        ),
        migrations.AlterModelTable(
            name='problemcollectionitem',
            table='a_psat_problem_collection_item',
        ),
        migrations.AlterModelTable(
            name='problemcomment',
            table='a_psat_problem_comment',
        ),
        migrations.AlterModelTable(
            name='problemcommentlike',
            table='a_psat_problem_comment_like',
        ),
        migrations.AlterModelTable(
            name='problemlike',
            table='a_psat_problem_like',
        ),
        migrations.AlterModelTable(
            name='problemmemo',
            table='a_psat_problem_memo',
        ),
        migrations.AlterModelTable(
            name='problemopen',
            table='a_psat_problem_open',
        ),
        migrations.AlterModelTable(
            name='problemrate',
            table='a_psat_problem_rate',
        ),
        migrations.AlterModelTable(
            name='problemsolve',
            table='a_psat_problem_solve',
        ),
        migrations.AlterModelTable(
            name='problemtag',
            table='a_psat_problem_tag',
        ),
        migrations.AlterModelTable(
            name='problemtaggeditem',
            table='a_psat_problem_tagged_item',
        ),
    ]
