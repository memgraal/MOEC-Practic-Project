import django.db.models
from django.conf import settings


class AuditLog(django.db.models.Model):

    class Actions(django.db.models.TextChoices):
        LOGIN = "login", "Вход"
        LOGOUT = "logout", "Выход"
        CREATE = "create", "Создание"
        UPDATE = "update", "Изменение"
        DELETE = "delete", "Удаление"
        READ = "read", "Просмотр"

    user = django.db.models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
    )

    action = django.db.models.CharField(
        max_length=30,
        choices=Actions.choices,
    )

    model_name = django.db.models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    object_id = django.db.models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ip_address = django.db.models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = django.db.models.TextField(
        null=True,
        blank=True,
    )

    created_at = django.db.models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action}"
