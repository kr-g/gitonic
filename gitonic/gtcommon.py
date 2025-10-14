
import logging

EXPERT_LOG = "expert"
REPO_LOG = "repo"

logex = logging.getLogger(EXPERT_LOG)
# todo config debgu for more detailed logging?
logex.setLevel(logging.INFO)

logrepo = logging.getLogger(REPO_LOG)
logrepo.setLevel(logging.INFO)

#


def _log(level, *args):
    if logex.isEnabledFor(level):
        logex.log(level, *args)

#


def log(*args):
    _log(logging.INFO, args)


def logi(*args):
    _log(logging.INFO, args)


def logd(*args):
    _log(logging.DEBUG, args)


def logw(*args):
    _log(logging.WARNING, args)


def loge(*args):
    _log(logging.ERROR, args)


def logc(*args):
    _log(logging.CRITICAL, args)

#


def print_t(*args):
    _log(logging.DEBUG, args)


def print_w(*args):
    _log(logging.WARNING, args)


def print_e(*args):
    _log(logging.ERROR, args)


def print_c(*args):
    _log(logging.CRITICAL, args)
