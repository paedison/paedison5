import csv
import traceback

import django.db.utils
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from a_common.utils import detect_encoding


def create_instance_get_messages(file_name: str, model: any) -> dict:
    model_name = model._meta.model_name
    update_list = []
    create_list = []
    update_count = 0
    create_count = 0
    create_message = ''
    update_message = ''
    error_message = ''
    encoding = detect_encoding(file_name)

    with open(file_name, 'r', encoding=encoding) as file:
        csv_data = csv.DictReader(file)
        for row in csv_data:
            row: dict
            try:
                fields = list(csv_data.fieldnames)
                instance = model.objects.get(id=row['id'])
                fields_not_match = any(str(getattr(instance, field)) != row[field] for field in fields)
                if fields_not_match:
                    for field, value in row.items():
                        setattr(instance, field, value)
                    update_list.append(instance)
                    update_count += 1
            except model.DoesNotExist:
                create_list.append(model(**row))
                create_count += 1

        try:
            with transaction.atomic():
                if create_list:
                    model.objects.bulk_create(create_list)
                    create_message = f'Successfully created {create_count} {model_name} instances.'

                if update_list:
                    fields = list(csv_data.fieldnames)
                    fields.remove('id')
                    model.objects.bulk_update(update_list, fields)
                    update_message = f'Successfully updated {update_count} {model_name} instances.'
                if not create_list and not update_list:
                    error_message = f'No changes were made to {model_name} instances.'
        except django.db.utils.IntegrityError:
            traceback_message = traceback.format_exc()
            print(traceback_message)
            error_message = 'An error occurred during the transaction.'

        return {
            'create': create_message,
            'update': update_message,
            'error': error_message,
        }


class Command(BaseCommand):
    help = 'Update Score Database'

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
