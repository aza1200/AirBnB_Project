from django.urls import path
from rooms import views as room_views

app_name = "core"

urlpatterns = [
    path("",room_views.HomeView.as_view(),name="home")
    #path("",room_views.all_rooms,name="home")
]

#path 는 오로지 url 그리고 함수만 가집니다..!!!!