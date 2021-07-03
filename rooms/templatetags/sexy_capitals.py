from django import template
#template 엔진 임포트

register = template.Library()
#library instance 얻어옴

@register.filter
def sexy_capitals(value):
    return value.capitalize()