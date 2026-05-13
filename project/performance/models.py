import django.db.models as models


class SystemMetrics(models.Model):
    timestamp = models.DateTimeField()

    total_requests = models.IntegerField()
    error_requests = models.IntegerField()
    avg_response_time = models.FloatField()

    class Meta:
        db_table = "system_metrics"
