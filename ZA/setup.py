from urllib2 import urlopen, URLError

from WiseAnn import *


def export(username, addr="127.0.0.1:8000", app="ZA"):
    try:
        u = "http://%s/%s/api/export/%s" % (addr, app, username)
        print(">>> [ZA.setup.export] Send request: %s" % u)
        f = urlopen(u, "password=%s" % TRUTH)
        print(">>> [ZA.setup.export] Recv response: %s" % f.read(500))
    except URLError as e:
        print(">>> [ZA.setup.export] Error message: %s" % e.reason)


def reset(addr="127.0.0.1:8000", app="ZA"):
    try:
        u = "http://%s/%s/api/reset/" % (addr, app)
        print(">>> [ZA.setup.reset] Send request: %s" % u)
        f = urlopen(u, "password=%s" % TRUTH)
        print(">>> [ZA.setup.reset] Recv response: %s" % f.read(500))
    except URLError as e:
        print(">>> [ZA.setup.reset] Error message: %s" % e.reason)


if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        print("[Usage] python setup.py function [arg1=127.0.0.1:8000] [arg2=ZA]")
        print("      - function : reset, export")

    elif argv[1] == "reset":
        if len(argv) > 3:
            reset(argv[2], argv[3])
        elif len(argv) > 2:
            reset(argv[2])
        else:
            reset()

    elif argv[1] == "export":
        if len(argv) > 4:
            export(argv[2], argv[3], argv[4])
        elif len(argv) > 3:
            export(argv[2], argv[3])
        elif len(argv) > 2:
            export(argv[2])

    else:
        print("[Usage] python setup.py function [arg1=127.0.0.1:8000] [arg2=ZA]")
        print("      - function : reset, export")
