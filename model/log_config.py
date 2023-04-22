import sys
from pathlib import Path

from model.error import LogError, NewLogConfigValueTypeError


def class_to_dict(class_dict):
    result = {}
    for value in class_dict.values():
        result[value.name] = value.factory()
    return result


class Formatter(object):
    default_fmt = "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s"
    default_date_fmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self, name, fmt=default_fmt, date_fmt=default_date_fmt):
        self._name = name
        self.format = fmt
        self.date_format = date_fmt

    @property
    def name(self):
        return self._name

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format = value

    @property
    def date_format(self):
        return self._date_format

    @date_format.setter
    def date_format(self, value):
        self._date_format = value

    def factory(self):
        return {"formatter": self.format, "datefmt": self.date_format}


class Handler(object):
    CLASS_HANDLER = ""

    def __init__(self, name, formatter, level):
        self.formatter = formatter
        self.level = level
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def formatter(self):
        return self._formatter

    @formatter.setter
    def formatter(self, value):
        if isinstance(value, Formatter):
            self._formatter = value
        else:
            raise NewLogConfigValueTypeError("Handler.formatter注入错误", Formatter.__name__, value.__class__.__name__)

    @property
    def all_level(self):
        return "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if value in self.all_level:
            self._level = value
        else:
            raise LogError("handler选择level错误，没有此level: " + value)

    def factory(self):
        return {"class": self.__class__.CLASS_HANDLER, "formatter": self.formatter.name, "level": self.level}


class StreamHandler(Handler):
    CLASS_HANDLER = "logging.StreamHandler"

    def __init__(self, name, formatter, level, stream):
        super().__init__(name, formatter, level)
        self.stream = stream

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        if ("write" in type(value).__dict__) and ("flush" in type(value).__dict__):
            self._stream = value
        else:
            raise NewLogConfigValueTypeError("StreamHandler.stream注入错误", "File", value.__class__.__name__)

    def factory(self):
        result = super().factory()
        result["stream"] = self.stream
        return result


class FileHandler(Handler):
    CLASS_HANDLER = "logging.FileHandle"

    def __init__(self, name, formatter, level, filename):
        super().__init__(name, formatter, level)
        self.filename = filename

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if isinstance(value, Path) and value.parent.exists():
            self._filename = value
        elif isinstance(value, str) and Path(value).parent.exists():
            self.filename = value
        else:
            raise LogError("FileHandler.filename错误，路径不存在")

    @property
    def mode(self):
        return "w"

    @property
    def encoding_type(self):
        return "utf-8"

    def factory(self):
        result = super().factory()
        result["filename"] = self.filename
        result["mode"] = self.mode
        result["encoding"] = self.encoding_type
        return result


class Root(object):
    def __init__(self, level="NOTSET"):
        self._level = level
        self._handlers = {}

    @property
    def level(self):
        return self._level

    @property
    def all_level(self):
        return "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"

    @property
    def handlers(self):
        return self._handlers

    @handlers.setter
    def handlers(self, value):
        if isinstance(value, Handler):
            self._handlers[value.name] = value
        else:
            raise NewLogConfigValueTypeError("LogConfig.handlers注入失败", Handler.__name__, value.__class__.__name__)

    def factory(self):
        return {"level": self.level, "handlers": list(map(lambda handler: handler.name, self.handlers.values()))}


class LogConfig(object):
    def __init__(self):
        self._formatters = {}
        self._handlers = {}
        self.formatters = Formatter("Default")
        self.handlers = StreamHandler("Default", self.formatters["Default"], "NOTSET", sys.stdout)
        root = Root()
        root.handlers = self.handlers["Default"]
        self._root = root

    @property
    def version(self):
        return 1

    @property
    def disable_existing_loggers(self):
        return False

    @property
    def formatters(self):
        return self._formatters

    @formatters.setter
    def formatters(self, value):
        if isinstance(value, Formatter):
            self._formatters[value.name] = value
        else:
            raise NewLogConfigValueTypeError("LogConfig.formatters注入失败", Formatter.__name__, value.__class__.__name__)

    @property
    def handlers(self):
        return self._handlers

    @handlers.setter
    def handlers(self, value):
        if isinstance(value, Handler):
            self._handlers[value.name] = value
        else:
            raise NewLogConfigValueTypeError("LogConfig.handlers注入失败", Handler.__name__, value.__class__.__name__)

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        if isinstance(value, Root):
            self._root = value
        else:
            raise NewLogConfigValueTypeError("LogConfig.root注入失败", Root.__name__, value.__class__.__name__)

    def factory(self):
        return {"version": self.version,
                "disable_existing_loggers": self.disable_existing_loggers,
                "formatters": class_to_dict(self.formatters),
                "handlers": class_to_dict(self.handlers),
                "root": self.root.factory()
                }
