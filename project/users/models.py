import django.db.models
import django.contrib.auth.models
import django.contrib.auth.base_user

import users.managers


class User(
    django.contrib.auth.base_user.AbstractBaseUser,
    django.contrib.auth.models.PermissionsMixin,
):

    class Types(django.db.models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        CLIENT = 'client', 'Клиент'

    email = django.db.models.EmailField(unique=True)
    type = django.db.models.CharField(
        max_length=20,
        choices=Types.choices,
        default=Types.CLIENT,
    )
    is_active = django.db.models.BooleanField(default=True)
    is_staff = django.db.models.BooleanField(default=False)
    objects =   users.managers.UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Client(User):
    name = django.db.models.CharField(max_length=255)
    surname = django.db.models.CharField(max_length=255)
    contact_info = django.db.models.CharField(max_length=255)
    registration_date = django.db.models.DateTimeField(auto_now_add=True)

    objects = users.managers.ClientManager()

    class Meta:
        db_table = 'clients'

    def save(self, *args, **kwargs):
        self.type = User.Types.CLIENT
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} {self.surname} <{self.email}>'
