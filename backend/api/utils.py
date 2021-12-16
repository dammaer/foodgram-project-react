from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib.colors import black, red
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from recipes.models import RecipeIngredient


def generate_pdf_shopping_list(user):
    shopping_list = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
    ).order_by().annotate(Sum('amount'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.pdf"'
    )
    pdfmetrics.registerFont(
        TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8')
    )
    page = Canvas(filename=response)
    page.setFont('DejaVuSerif', 24)
    page.setFillColor(red)
    page.drawString(210, 800, 'Список покупок')
    height = 760
    for idx, ingr in enumerate(shopping_list, start=1):
        page.setFont('DejaVuSerif', 16)
        page.setFillColor(black)
        page.drawString(60, height, text=(
            f'{idx}. {ingr["ingredient__name"]} - {ingr["amount_sum"]} '
            f'{ingr["ingredient__measurement_unit"]}'
        ))
        height -= 30
        if height <= 40:
            page.showPage()
            height = 800
    page.save()
    return response
