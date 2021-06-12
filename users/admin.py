from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rooms import models as room_models
from . import models

# from . 은 같은 경로에 있는것 불러오는 거임

# Register your models here.

class RoomInline(admin.TabularInline):
    model = room_models.Room

@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""

    inlines = (RoomInline,)

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Profile", {"fields": ("avatar", "gender", "bio","birthdate","language","currency","superhost",)}),
    )

    list_filter = UserAdmin.list_filter+ (
        "superhost",
    )

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "language",
        "currency",
        "superhost",
        "is_staff",
        "is_superuser",
    )
#admin.site.register(models.User,CustomUserAdmin) 이랑 같은 효과 decorator

