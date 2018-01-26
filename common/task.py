from datetime import datetime
from common.time import get_now


class Task:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print('[INIT] {} [{}]'.format(self.name, get_now(fmt='%H:%M:%S')))
        self.t1 = datetime.now()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = datetime.now()
        dur = self.t2 - self.t1
        print('[EXIT] {} [{}] ({} elapsed)'.format(self.name, get_now(fmt='%H:%M:%S'), dur))
        print()
