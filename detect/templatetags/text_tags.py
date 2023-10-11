import re

from django import template
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines

register = template.Library()


def paragraph_format(paragraph: str) -> str:
    lines = paragraph.split("\n")
    result = []
    for line in lines:
        if line.startswith('##bordered-image:'):
            # todo изображения в рамке
            continue
        elif line.startswith('##image-caption:'):
            # todo подписи изображений
            continue
        if line.startswith('##image:'):
            # todo изображения в исходной форме (для формул)
            continue
        elif line.startswith('##bold-line:'):
            # todo подглавы в теории
            continue
        elif line.startswith('##sub:'):
            # todo подстроки (исп. в формулах)
            continue
        elif line.startswith('##card-info-start:') or line.startswith('##card-info-end'):
            # todo дополнительные информационные карточки
            continue
        result.append(f'<div class="text-indent">{line}</div>')
    return "".join(result)


@register.filter('text_format')
def text_format(text: str) -> str:
    text = str(normalize_newlines(text))
    paras = re.split('\n{2,}', text)
    result = '<br>'.join(paragraph_format(p) for p in paras)
    return mark_safe(result)
