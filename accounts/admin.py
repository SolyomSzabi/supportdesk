from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, User

admin.site.register(Company)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Company", {"fields": ("company", "role")}),)
    list_display = ("username", "email", "company", "role", "is_staff")