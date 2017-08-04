from urllib2 import urlopen, URLError

from WiseAnn import *


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

    if len(argv) > 2:
        reset(argv[1], argv[2])
    elif len(argv) > 1:
        reset(argv[1])
    else:
        reset()
