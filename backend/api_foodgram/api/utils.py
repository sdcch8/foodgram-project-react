from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import RecipeIngredient


def download_shopping_cart(self, request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=self.request.user
    )

    ingredients = (ingredients.order_by('ingredient__name')
                              .values('ingredient__name',
                                      'ingredient__measurement_unit')
                              .annotate(amount=Sum('amount'))
                   )

    export = []
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['amount']
        export.append(f'{name}: {amount} {measurement_unit}\n')

    response = HttpResponse(export, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="list.txt"'

    return response
