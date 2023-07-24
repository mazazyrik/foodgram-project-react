import csv
from backend.foodgram_backend.recipes.models import Ingredient

DJANGO_SETTINGS_MODULE = 'backend.foodgram_backend.foodgram_backend'

with open('data/ingredients.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # пропустить заголовок

    for row in reader:
        data = {
            'name': row[0],
            'measurement_unit': row[1],
        }

        # создать экземпляр модели Django на основе преобразованных данных
        obj = Ingredient(**data)

        # сохранить экземпляр модели в базе данных Django
        obj.save()
