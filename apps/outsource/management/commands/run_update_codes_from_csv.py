import csv
import os

from django.core.management.base import BaseCommand, CommandError

from apps.outsource.models import Organization


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('username', type=str,
                            help='логин пользователя, от имени которого будут выполняться некоторые операции')
        parser.add_argument('--path', type=str, help='путь к справочнику по замене кодов',
                            default='/home/wfm/outsourcing/org_codes.csv')
        parser.add_argument('--delimiter', type=str, help='разделитель ячеек', default=',')
        parser.add_argument('--debug', type=bool, default=False, help='режим отладки')

    def handle(self, *args, **options):
        # Read file
        file_path = options.get('path')
        if not file_path:
            raise CommandError('Provide path to file')

        if not os.path.exists(file_path):
            raise CommandError(f'No file at location {file_path}')

        delimiter = options.get('delimiter')

        rows_success = 0  # rows without errors
        rows_errors = 0   # rows with errors, e.g. object with code not found
        rows_updated = 0  # rows resulted in object update
        rows_skipped = 0  # rows already used to update an object
        rows_total = 0    # rows

        with open(file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
            for row in csv_reader:
                rows_total += 1
                old_code = row['old_code']
                new_code = row['new_code']

                # Try to get an object for update
                organization = Organization.objects.filter(code=old_code).first()
                if organization:
                    try:
                        organization.code = new_code
                        organization.save(update_fields=('code',))
                        rows_updated += 1
                        rows_success += 1
                    except:
                        rows_errors += 1
                # Object for update not found. Check if there is an object with the new_code
                # in the code field (~ already updated object)
                else:
                    organization = Organization.objects.filter(code=new_code).first()
                    if organization:
                        rows_skipped += 1
                        rows_success += 1
                    else:
                        rows_errors += 1

            print(f'{rows_total} rows were processed, of which')
            print(f'Success: {rows_success}, errors: {rows_errors}')
            print(f'{rows_updated} were used to update organizations, {rows_skipped} were skipped.')
