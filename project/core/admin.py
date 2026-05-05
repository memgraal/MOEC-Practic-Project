from django.contrib import admin

from core.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "model_name",
        "object_id",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "action",
        "model_name",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "model_name",
        "object_id",
        "ip_address",
        "user_agent",
    )

    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "ip_address",
        "user_agent",
        "created_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    list_per_page = 50

    fieldsets = (
        ("Основное", {
            "fields": (
                "user",
                "action",
                "created_at",
            )
        }),
        ("Объект", {
            "fields": (
                "model_name",
                "object_id",
            )
        }),
        ("Информация о запросе", {
            "fields": (
                "ip_address",
                "user_agent",
            )
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
