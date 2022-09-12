import main
import os


def get_path(file):
    with open(os.path.join(main.root, "Config", "data_path.txt")) as f:
        path = f.readline()

    return os.path.join(path, file)
