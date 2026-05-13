import os
from datetime import datetime

import requests
from django.utils.timezone import now
from django.db import connection

from performance.models import SystemMetrics
from project.project.settings import METRICS_URL



def db_backup():

    _db_conf = connection.settings_dict
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    os.makedirs("backups", exist_ok=True)

    file_path = os.path.join("backups", f"{_db_conf['NAME']}_{now}.sql")

    command = f"mysqldump -h {_db_conf['HOST']} -u {_db_conf['USER']} -p{_db_conf['PASSWORD']} {_db_conf['NAME']} > {file_path}"

    os.system(command)


def query(q):
    try:
        r = requests.get(METRICS_URL, params={"query": q})
        data = r.json()
        return float(data["data"]["result"][0]["value"][1])
    except:
        return 0


def collect_metrics():
    total_requests = query("django_http_requests_total_by_method_total")
    errors = query('django_http_responses_total_by_status_total{status="404"}')

    SystemMetrics.objects.create(
        timestamp=now(),
        total_requests=total_requests,
        error_requests=errors,
        avg_response_time=0,  # потом добавим
    )