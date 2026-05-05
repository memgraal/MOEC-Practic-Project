import os
from datetime import datetime

from django.db import connection



def db_backup():

    _db_conf = connection.settings_dict
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    os.makedirs("backups", exist_ok=True)

    file_path = os.path.join("backups", f"{_db_conf['NAME']}_{now}.sql")

    command = f"mysqldump -h {_db_conf['HOST']} -u {_db_conf['USER']} -p{_db_conf['PASSWORD']} {_db_conf['NAME']} > {file_path}"

    os.system(command)
