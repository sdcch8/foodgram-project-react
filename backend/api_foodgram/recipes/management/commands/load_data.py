import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('recipes/data/ingredients.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )

        with open('recipes/data/tags.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                name, color, slug = row
                Tag.objects.get_or_create(
                    name=name, color=color, slug=slug
                )
