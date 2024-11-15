from datetime import datetime


def get_utcnow_str():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
