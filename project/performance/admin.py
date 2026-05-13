from django.contrib import admin
from performance.models import SystemMetrics


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "timestamp",
        "total_requests",
        "error_requests",
        "avg_response_time",
    )

    list_filter = (
        "timestamp",
    )

    search_fields = (
        "id",
    )

    ordering = ("-timestamp",)

    readonly_fields = (
        "timestamp",
        "total_requests",
        "error_requests",
        "avg_response_time",
    )

    list_per_page = 50
