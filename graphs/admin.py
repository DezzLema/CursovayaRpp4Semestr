from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Graph

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Graph)