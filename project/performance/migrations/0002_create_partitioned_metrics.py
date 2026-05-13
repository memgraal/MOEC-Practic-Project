from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("performance", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id BIGINT AUTO_INCREMENT,
                timestamp DATETIME NOT NULL,
                total_requests INT,
                error_requests INT,
                avg_response_time FLOAT,
                PRIMARY KEY (id, timestamp)
            )
            PARTITION BY RANGE (TO_DAYS(timestamp)) (
                PARTITION p202605 VALUES LESS THAN (TO_DAYS('2026-06-01')),
                PARTITION p202606 VALUES LESS THAN (TO_DAYS('2026-07-01')),
                PARTITION pmax VALUES LESS THAN MAXVALUE
            );
            """,
            reverse_sql="DROP TABLE system_metrics;",
        ),
    ]