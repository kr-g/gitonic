import sys
import os
import json

from const import F_CONFIG, PATH
from file import FileStat

#


def get_path(fnam=F_CONFIG):
    fp = os.path.join("~", PATH)
    if fnam:
        fp = os.path.join(fp, fnam)
    fp = os.path.expanduser(fp)
    return fp

#


def exists_settings(fnam=F_CONFIG):
    fp = get_path(fnam)
    return FileStat(fp).exists()


def load_settings(fnam=F_CONFIG):
    fp = get_path(fnam)
    try:
        with open(fp) as f:
            return json.load(f)
    except Exception as ex:
        print("load config", ex, file=sys.stderr)

    return {}


def save_settings(cfg, fnam=F_CONFIG):
    fp = get_path(fnam)
    with open(fp, "w") as f:
        return json.dump(cfg, f, indent=4)

#


def elements_iter(adict, keypath=[]):
    """deep elements iterator"""

    def _iter(x):
        return x.items()

    if type(adict) is list:
        _iterfunc = enumerate
    else:
        _iterfunc = _iter

    for k, v in _iterfunc(adict):
        keypath = [*keypath, k]

        if type(v) in [list, dict]:
            yield from elements_iter(v, keypath)
            continue

        def setr(nv):
            adict[k] = nv

        yield keypath, v, setr


def replace_settings(project_settings, base_settings):
    """replace base setting generics from project settings"""
    base_settings = dict(base_settings)
    # not the most effective way ...
    for k, v in project_settings.items():
        for kk, vv, setr in elements_iter(base_settings):
            if type(vv) is not str:
                continue
            r = "{" + k + "}"
            if vv.find(r) >= 0:
                setr(vv.replace(r, v))

    return base_settings

#


class Config(object):
    def __init__(self, fnam=F_CONFIG):
        self.fnam = fnam
        self.conf = None

    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self.fnam) + "," + str(self.conf) + ")"

    def __len__(self):
        return len(self.conf)

    def exists(self):
        return exists_settings(self.fnam)

    def load(self):
        self.conf = load_settings(self.fnam)
        return self

    def save(self):
        assert self.conf
        save_settings(self.conf, self.fnam)

    def set_val(self, key, val):
        self.conf[key] = val

    def get_val(self, key, defval=None):
        return self.get(key, defval)

    def get(self, key, defval=None):
        return self.conf.get(key, defval)

    def getint(self, key, defval):
        try:
            return int(self.get(key, defval))
        except Exception as ex:
            print("config key", key, ex, file=sys.stderr)

        return int(defval)

    def getbool(self, key, defval):
        try:
            return str(self.get(key, defval)).upper() == "TRUE"
        except Exception as ex:
            print("config key", key, ex, file=sys.stderr)

        return str(defval).upper() == "TRUE"

#
