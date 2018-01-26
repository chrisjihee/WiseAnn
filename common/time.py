from datetime import datetime


def get_now(fmt='%Y%m%d_%H%M%S'):
    return datetime.strftime(datetime.now(), fmt)
