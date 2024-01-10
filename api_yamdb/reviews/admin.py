from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import (
    Category,
    Comment,
    Genre,
    MyUser,
    Review,
    Title,
)


@admin.register(Category, Comment, Genre, Review, Title)
class CommonAdmin(admin.ModelAdmin):
    pass


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
