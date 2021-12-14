import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients data to DB'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to csv file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(name=name,
                                                 measurement_unit=unit)
            self.stderr.write(self.style.SUCCESS('SUCCESS'))
