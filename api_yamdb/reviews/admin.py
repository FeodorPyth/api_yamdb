from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser


class MyUserAdmin(UserAdmin):
    model = MyUser

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Роль пользователя',
            {
                'fields': (
                    'role',
                )
            }
        )
    )


admin.site.register(MyUser, MyUserAdmin)
