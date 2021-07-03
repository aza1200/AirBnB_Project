import datetime
from django import template
from reservations import models as reservation_models
#template 엔진 임포트

register = template.Library()
#library instance 얻어옴

@register.simple_tag
def is_booked(room,day):
    if day.number == 0:
        return
    try:
        date = datetime.datetime(year=day.year,month =day.month,day=day.number)
        reservation_models.BookedDay.objects.get(day=date,reservation__room= room)
        return True
    except reservation_models.BookedDay.DoesNotExist:
        return False

    return False


# {% is_booked room day as is_booked bool %}
# room,day 를 인자로 is_booked 를 호출하고 있고 그 결과를 is_booked_bool 변수에 저장을 해줄것임


