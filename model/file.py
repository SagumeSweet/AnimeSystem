import os
from error import PathError


class Paths(object):
    def __init__(self, path):
        if os.path.exists(path) and os.path.isabs(path):
            raise PathError("文件路径不正确", path)
        else:
            self.full_path = path

    @property
    def path(self):
        return os.path.split(self.full_path)[0]

    @property
    def base_path(self):
        return os.path.split(self.full_path)[1]


class Files(object):
    def __init__(self, path):
        if isinstance(path, Paths):
            self.full_path = path
        else:
            raise PathError("")