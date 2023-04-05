class Error(Exception):
    def __str__(self):
        print(self.__class__.__name__ + ":")

    __repr__ = __str__


class PathError(Error):
    def __init__(self, info, path):
        self.info = info
        self.path = path

    def __str__(self):
        super().__str__()
        print(self.info)
        print("错误路径：", self.path)


class LogError(Error):
    def __init__(self, info):
        self.info = info

    def __str__(self):
        super().__str__()
        print(self.info)


class NewLogConfigValueTypeError(LogError):
    def __init__(self, info, correct_type, error_type):
        super().__init__(info)
        self.correct_type = correct_type
        self.error_type = error_type

    def __str__(self):
        super().__str__()
        print("正确数据类型：", self.correct_type)
        print("错误数据类型：", self.error_type)
