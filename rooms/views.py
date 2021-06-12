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
    room_type = int(request.GET.get("room_type",0))
    price = int(request.GET.get("price",0))
    guests = int(request.GET.get("guests",0))
    bedrooms = int(request.GET.get("bedrooms",0))
    beds = int(request.GET.get("beds",0))
    baths = int(request.GET.get("baths",0))

    instant    = bool(request.GET.get("instant",False))
    superhost = bool(request.GET.get("superhost",False))

    s_amenities = request.GET.getlist("amenities")
    f_facilities = request.GET.getlist("facilities")



    form = {
        "city": city,
        "s_country": country,
        "s_room_type": room_type,
        "price":price,
        "guests":guests,
        "bedrooms":bedrooms,
        "beds":beds,
        "baths":baths,
        "s_amenities":s_amenities,
        "s_facilities":f_facilities,
        "instant" : instant,
        "superhost" : superhost,
    }

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()


    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities" : amenities,
        "facilities" : facilities,
    }

    filter_args = {}

    if city != "Anywhere":
        filter_args["city__startswith"] = city

    filter_args["country"] = country

    if room_type != 0:
        filter_args["room_type__pk"] = room_type

    if price != 0:
        filter_args["price__lte"] = price

    if guests != 0:
        filter_args["guests__gte"] = guests

    if bedrooms != 0:
        filter_args["bedrooms__gte"] = bedrooms

    if beds != 0:
        filter_args["beds__gte"] = beds

    if baths != 0:
        filter_args["baths__gte"] =baths


    if instant is True:
        filter_args["instant_book"] = True

    if superhost is True:
        filter_args["host__superhost"] = True

    rooms = models.Room.objects.filter(**filter_args)

    if len(s_amenities) > 0:
        for s_amenity in s_amenities:
            rooms = rooms.filter(amenities__pk=int(s_amenity))

    if len(f_facilities) > 0:
        for f_facility in f_facilities:
            rooms = rooms.filter(facilities__pk = int(f_facility))


    print(filter_args)
    return render(request,"rooms/search.html",
        {**form ,**choices,"rooms":rooms}
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