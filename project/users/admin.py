import django.contrib.admin
import django.contrib.auth.admin

from users.models import User, Client


@django.contrib.admin.register(User)
class UserAdmin(django.contrib.auth.admin.UserAdmin):
    model = User

    list_display = (
        'id',
        'email',
        'type',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_login',
    )

    list_filter = (
        'type',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'email',
    )

    ordering = (
        'id',
    )

    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'email',
                    'password',
                    'type',
                ),
            },
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (
            'Системная информация',
            {
                'fields': (
                    'last_login',
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': (
                    'wide',
                ),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'type',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )


@django.contrib.admin.register(Client)
class ClientAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'surname',
        'email',
        'contact_info',
        'registration_date',
    )

    list_filter = (
        'registration_date',
    )

    search_fields = (
        'name',
        'surname',
        'email',
        'contact_info',
    )

    ordering = (
        'id',
    )

    readonly_fields = (
        'registration_date',
        'last_login',
    )

    fieldsets = (
        (
            'Данные клиента',
            {
                'fields': (
                    'name',
                    'surname',
                    'contact_info',
                    'registration_date',
                ),
            },
        ),
        (
            'Учётная запись',
            {
                'fields': (
                    'email',
                    'password',
                    'last_login',
                ),
            },
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'type',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
    )