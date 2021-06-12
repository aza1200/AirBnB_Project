from django.views.generic import ListView,DetailView
from django.shortcuts import render
from django.utils import timezone
from django_countries import countries
from django.http import Http404
from django.urls import reverse
from . import models


class HomeView(ListView):

    """ HomeView Definition """

    model = models.Room
    paginate_by = 10
    ordering = "created"
    paginate_orphans = 10
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now

        return context

class RoomDetail(DetailView):

    """Room Detail Definition"""

    model = models.Room

def search(request):
    city = request.GET.get("city","Anywhere")
    city = str.capitalize(city)
    country = request.GET.get("country","KR")
    room_tpye = int(request.GET.get("room_type",0))
    room_types = models.RoomType.objects.all()


    form = {
        "city": city,
        "s_country": country,
        "s_room_type": room_tpye,
    }

    choices = {
        "countries": countries,
        "room_types": room_types,
    }

    return render(request,"rooms/search.html",
        {**form ,**choices}
    )

# def room_detail(request,pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, "rooms/detail.html", {'room': room})
#     except models.Room.DoesNotExist:
#         return redirect(reverse("core:home"))
#         #raise Http404()
#         #url 대신 reverse 사용 ㄱ




















# # Create your views here.
#
# def all_rooms(request):
#     page = request.GET.get("page",1)
#     room_list = models.Room.objects.all() #게으른 놈이라는 것을 기억하자!
#     paginator = Paginator(room_list,10,orphans=5) #uppercase, lowercase 비교하자! #orphans 장고 문서를 읽어보자 어흥
#
#     try:
#         rooms = paginator.get_page(int(page))
#         return render(request, "rooms/home.html", context={"page": rooms})
#     except Exception:
#         rooms = paginator.page(10)
#         return redirect("/")
#
#     #print(vars(rooms.paginator))
#


#
# def all_rooms(request):
#     page = request.GET.get("page",1)
#     page = int(page or 1)
#     page_size = 10
#     limit = page_size* int(page)
#     offset = limit - page_size
#     all_rooms = models.Room.objects.all()[offset:limit]
#     page_count = ceil(models.Room.objects.count() / page_size)
#
#
#     return render(request,"rooms/home.html",context={
#         "rooms":all_rooms,
#         "page":page,
#         "page_count":page_count,
#         "page_range": range(1,page_count),
#     })