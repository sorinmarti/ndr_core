import os

from django.core.management.base import BaseCommand

from ndr_core_api.ndr_core_api_helpers import get_api_config


class Command(BaseCommand):
    help = 'Initializes an ndr-core app'

    def add_arguments(self, parser):
        # parser.add_argument('which_test', type=str)
        pass

    def handle(self, *args, **options):
        app_name = get_api_config()["app_name"]
        self.stdout.write(f'Creating {app_name} app')

        if os.path.isdir(app_name):
            self.stdout.write(self.style.ERROR(f'folder "{app_name}" already exists.'))
            return

        try:
            os.mkdir(app_name)
        except OSError:
            self.stdout.write(self.style.ERROR("Creation of the directory %s failed" % app_name))
            return

        subdirectories = ['templates', f'templates/{app_name}']
        for sub in subdirectories:
            try:
                os.mkdir(f"{app_name}/{sub}")
            except OSError:
                self.stdout.write(self.style.ERROR(f'Could not create subdirectory "{sub}". Exiting.'))
                return
            else:
                self.stdout.write(self.style.SUCCESS(f'Created subdirectory "{sub}"'))

        # Sub directories are created: copy and modify init files
        files = [('urls.py', 'new_app_urls.py'),
                 (f'templates/{app_name}/base.html', 'new_app_base.html'),
                 (f'templates/{app_name}/index.html', 'new_app_index.html'),
                 ('views.py', 'new_app_views.py'),
                 ('forms.py', 'new_app_forms.py'),
                 ('tables.py', 'new_app_tables.py'),
                 ('_TODO.txt', 'new_app_todo.txt'),
                 ]



        self.stdout.write(self.style.SUCCESS('ndr-core initialized'))
