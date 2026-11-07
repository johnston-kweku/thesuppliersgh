from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.



@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = [
        'username',
        'full_name',
        'role',
        'public_id',
        'phone_number',
        'email',
        'is_active'
    ]

    list_editable = [
        'is_active'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password',
            ),
        }),
        ('Personal information', {
            'fields': (
                'full_name',
                'email',
                'phone_number',
            ),
        }),
        ('The Suppliers GH', {
            'fields': (
                'role',
            ),
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Important dates', {
            'fields': (
                'last_login',
                'date_joined',
            ),
        }),
    )

    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': (
            'username',
            'password1',
            'password2',
            'full_name',
            'email',
            'phone_number',
            'role',
        ),
    }),
)
