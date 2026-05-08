import django.contrib.admin

from core.models import AuditLog
from core.utils import write_audit_log


class AuditAdminMixin:
    model_name = None

    def save_model(self, request, obj, form, change):
        action = (
            AuditLog.Actions.UPDATE
            if change
            else AuditLog.Actions.CREATE
        )

        super().save_model(request, obj, form, change)

        write_audit_log(
            request=request,
            action=action,
            model_name=self.model_name or obj.__class__.__name__,
            object_id=obj.pk,
        )

    def delete_model(self, request, obj):
        object_id = obj.pk
        model_name = self.model_name or obj.__class__.__name__

        super().delete_model(request, obj)

        write_audit_log(
            request=request,
            action=AuditLog.Actions.DELETE,
            model_name=model_name,
            object_id=object_id,
        )

    def delete_queryset(self, request, queryset):
        ids = list(queryset.values_list("pk", flat=True))
        model_name = self.model_name or queryset.model.__name__

        count = len(ids)

        super().delete_queryset(request, queryset)

        for object_id in ids:
            write_audit_log(
                request=request,
                action=AuditLog.Actions.DELETE,
                model_name=model_name,
                object_id=object_id,
            )

        django.contrib.admin.messages.success(
            request,
            f"Удалено объектов: {count}",
        )
