import os


def list_files(x, key=None):
    for (path, _, files) in sorted(os.walk(x)):
        for f in sorted(files):
            if key is None or key in f:
                yield os.path.join(path, f)
