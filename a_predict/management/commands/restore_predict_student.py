import csv
import traceback

import django.db.utils
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from a_common.utils import detect_encoding
from a_predict.models import Student


exam_id_list = [
    {'id': 1, 'ex': '프모', 'round': 1},
    {'id': 2, 'ex': '프모', 'round': 3},
    {'id': 3, 'ex': '프모', 'round': 4},
    {'id': 4, 'ex': '프모', 'round': 5},
    {'id': 5, 'ex': '프모', 'round': 6},
    {'id': 6, 'ex': '행시', 'round': 0},
]

department_id_list = []


def create_instance_get_messages() -> dict:
    model_name = 'Student'
    file_name = 'predict_student.csv'
    list_update = []
    list_create = []
    count_update = count_create = 0
    msg_create = msg_update = msg_error = ''
    encoding = detect_encoding(file_name)

    with open(file_name, 'r', encoding=encoding) as file:
        csv_data = csv.DictReader(file)
        fields = list(csv_data.fieldnames)
        verifying_fields = ['id', 'user_id', 'name', 'serial', 'password']
        for row in csv_data:
            row: dict
            if row['id']:
                try:
                    instance = Student.objects.get(id=row['id'])
                    fields_not_match = any(str(getattr(instance, field)) != row[field] for field in fields)
                    if fields_not_match:
                        for field, value in row.items():
                            setattr(instance, field, value)
                        list_update.append(instance)
                        count_update += 1
                except Student.DoesNotExist:
                    list_create.append(Student(**row))
                    count_create += 1

        try:
            with transaction.atomic():
                if list_create:
                    model.objects.bulk_create(list_create)
                    msg_create = f'Successfully created {count_create} {model_name} instances.'
                if list_update:
                    fields_update = fields.copy()
                    fields_update.remove('id')
                    model.objects.bulk_update(list_update, fields_update)
                    msg_update = f'Successfully updated {count_update} {model_name} instances.'
                if not list_create and not list_update:
                    msg_error = f'No changes were made to {model_name} instances.'
        except django.db.utils.IntegrityError:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            msg_error = 'An error occurred during the transaction.'

        return {
            'create': msg_create,
            'update': msg_update,
            'error': msg_error,
        }


class Command(BaseCommand):
    help = 'Update Database'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, help='Name of the target file')
        parser.add_argument('app_name', type=str, help='Name of the app containing the model')
        parser.add_argument('model_name', type=str, help='Name of the model')

    def handle(self, *args, **kwargs):
        file_name = kwargs['file_name']
        app_name = kwargs['app_name']
        model_name = kwargs['model_name']

        try:
            model = apps.get_model(app_label=app_name, model_name=model_name)
        except LookupError:
            self.stdout.write(self.style.ERROR(f"Model '{model_name}' not found in app '{app_name}'."))
            return

        messages = create_instance_get_messages(file_name, model)
        for key, message in messages.items():
            if message:
                self.stdout.write(self.style.SUCCESS(message))