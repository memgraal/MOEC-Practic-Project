from core.models import AuditLog


def write_audit_log(
    request,
    action,
    model_name=None,
    object_id=None,
):
    user = None
    if request.user.is_authenticated:
        user = request.user

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT"),
    )


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")