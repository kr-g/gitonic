# import sys
# import os
import logging
import logging.handlers
# import tempfile
# import queue

_level = logging.INFO

# _datefmt = "%Y.%m.%d %H:%M:%S"

# _format = "%(levelname)-8s %(message)s"
# _fileformat = "%(asctime)-8s %(levelname)s\t%(message)s"

_logger = None
# _filehandler = None


#
# https://docs.python.org/3/howto/logging-cookbook.html
#

# todo rework
# https://docs.python.org/3/library/logging.handlers.html#logging.handlers.QueueHandler
# https://docs.python.org/3/library/logging.handlers.html#queuelistener

class LogOutHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET, callb=None, name=None):
        super().__init__(level=level)

        frmt = logging.Formatter(
            "%(asctime)s %(levelname)s", datefmt="%Y.%m.%d %H:%M:%S")

        self.setFormatter(frmt)

        self.callback = callb
        self.name = name
        self._strip = False

    def __repr__(self):
        level = logging.getLevelName(self.level)
        return self.__class__.__name__ + f"( {self.name} {level})"

    def strip(self):
        self._strip = True
        return self

    @property
    def callback(self):
        return self._callb

    def _nil(self, *args):
        print("nil<<<", *args)

    @callback.setter
    def callback(self, callb=None):
        self._callb = callb if callb else self._nil
        return self

    def emit(self, record):

        args = [record.msg] if self._strip is False else []

        if record.args:
            args.extend(list(record.args))
        args = map(lambda x: str(x), args)

        # todo
        targs = record.args

        record.args = None
        if self._strip:
            tmesg = record.message
            record.message = None

        s = self.format(record)

        # todo
        record.args = targs
        if self._strip:
            record.message = tmesg

        self._callb("\t".join([s, *args]))

    def filter(self, record):
        # print("!!!!!!!!!!!!!", record.__dict__)
        return super().filter(record)

    def _filter_name(self, record):
        if self.name is None:
            return True

        # todo add extra field to record

        # print("filter", self.name==record.message, str(record))

        return record.message == self.name

    # todo refactor
    # to own class?

    def filter_on_name(self):

        if self.name:
            # print("enable filter name", self.name)
            self.filter = self._filter_name

        return self
#


# todo remove old coding below


# def setlevel(level=None, logtofile=False, opts=None, logname = None):
#     global _level, _logger

#     if level:
#         _level = level

#     if _logger is None:
#         # create logger
#         _logger = logging.getLogger(logname)

#         # create console handler and set level to debug
#         ch = logging.StreamHandler()
#         ch.setLevel(_level)

#         # create formatter
#         formatter = logging.Formatter(_format, datefmt=_datefmt)

#         # add formatter to ch
#         ch.setFormatter(formatter)

#         # add ch to logger
#         _logger.addHandler(ch)

#     for h in [_logger, *_logger.handlers]:
#         if h:
#             h.setLevel(_level)

#     if logtofile:
#         setlogfile(opts=opts)


# def setdebug():
#     setlevel(logging.DEBUG)


# def setlogfile(pnam=None, path=None, opts=None):
#     global _filehandler
#     if _filehandler:
#         return

#     if opts is None:
#         opts = {"maxBytes": 1024 * 1024, "backupCount": 7}

#     setlevel()

#     if pnam is None:
#         pnam = sys.argv[0]
#     if path is None:
#         path = tempfile.gettempdir()

#     pnam, _ = os.path.splitext(os.path.basename(pnam))

#     fnam = os.path.join(path, pnam, pnam + ".log")
#     # print("logfile",fnam)

#     os.makedirs(os.path.dirname(fnam), exist_ok=True)

#     _filehandler = logging.handlers.RotatingFileHandler(fnam, **opts)
#     _filehandler.setLevel(_level)

#     formatter = logging.Formatter(_fileformat, datefmt=_datefmt)
#     _filehandler.setFormatter(formatter)
#     _logger.addHandler(_filehandler)

#     return fnam


# def _flat(args):
#     fs = map(lambda x: str(x), args)
#     return " ".join(fs)


# def _log(level, args):
#     if _logger.isEnabledFor(level):
#         _logger.log(level, _flat(args))

# #


# def log(*args):
#     _log(logging.INFO, args)


# def logi(*args):
#     _log(logging.INFO, args)


# def logd(*args):
#     _log(logging.DEBUG, args)


# def logw(*args):
#     _log(logging.WARNING, args)


# def loge(*args):
#     _log(logging.ERROR, args)


# def logc(*args):
#     _log(logging.CRITICAL, args)

# #


# def print_t(*args):
#     _log(logging.DEBUG, args)


# def print_w(*args):
#     _log(logging.WARNING, args)


# def print_e(*args):
#     _log(logging.ERROR, args)


# def print_c(*args):
#     _log(logging.CRITICAL, args)


# create logger

# setlevel()
# todo remove old coding below
