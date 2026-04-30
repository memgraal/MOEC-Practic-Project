import django.contrib.auth.base_user

from users.querysets import UserQuerySet, ClientQuerySet


class UserManager(
    django.contrib.auth.base_user.BaseUserManager.from_queryset(UserQuerySet)
):
    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ):
        if not email:
            raise ValueError('Поле email обязательно')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ):
        extra_fields.setdefault('type', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class ClientManager(
    django.contrib.auth.base_user.BaseUserManager.from_queryset(ClientQuerySet)
):
    def create_client(
        self,
        email: str,
        password: str,
        name: str,
        surname: str,
        contact_info: str,
        **extra_fields,
    ):
        if not email:
            raise ValueError('Поле email обязательно')

        client = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            contact_info=contact_info,
            type='client',
            **extra_fields,
        )

        client.set_password(password)
        client.save(using=self._db)

        return client
