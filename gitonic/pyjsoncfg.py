import os
import sys

import re
import json


VERSION = "v0.0.6"


class _cfg_namespace:
    def __init__(self, cfg):

        self.__dict__.update(cfg)

        for k, v in self.__dict__.items():
            if isinstance(v, dict):
                self.__dict__.update({k: _cfg_namespace(v)})
            if isinstance(v, list):
                a = []
                for vv in v:
                    if isinstance(vv, list) or isinstance(vv, dict):
                        a.append(_cfg_namespace(vv))
                    else:
                        a.append(vv)
                self.__dict__.update({k: a})
            if isinstance(v, _cfg_namespace):
                self.__dict__.update({k: _cfg_namespace(v.__dict__)})

    def __iter__(self):
        for k, v in self.items():
            yield k

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, v):
        if isinstance(v, dict):
            v = _cfg_namespace(v)
        self.__dict__[key] = v

    def __delitem__(self, key):
        del self.__dict__[key]

    def update(self, dict_):
        self.__dict__.update(dict_)
        return self

    def items(self):
        return self.__dict__.items()

    def __repr__(self):
        d = self._dismantle(self.__dict__)
        return json.dumps(d)

    def _dismantle(self, dic):
        d = {}
        for k, v in dic.items():
            if isinstance(v, _cfg_namespace):
                d[k] = self._dismantle(v.__dict__)
            elif type(v) == dict:
                d[k] = self._dismantle(v)
            elif type(v) == list:
                a = []
                for o in v:
                    if isinstance(o, _cfg_namespace):
                        a.append(self._dismantle(o.__dict__))
                    elif type(o) == dict:
                        a.append(self._dismantle(o))
                    else:
                        a.append(o)
                d[k] = a
            else:
                d[k] = v
        return d

    def setdefault(self, key, default_val=None):
        if not key in self.__dict__:
            if type(default_val) == dict:
                self.__dict__[key] = self._dismantle(default_val)
            elif type(default_val) == list:
                a = []
                for o in default_val:
                    if type(o) == dict:
                        a.append(_cfg_namespace(self._dismantle(o)))
                    else:
                        a.append(o)
                self.__dict__[key] = a
            else:
                self.__dict__[key] = default_val
        return self.__dict__[key]

    def default(self, o):
        try:
            return self._dismantle(o.__dict__)
        except:
            return json.JSONEncoder.default(self, o)


class Config:

    DEFAULT_CONFIG_FILE = "cfg.json"

    # environment variables
    PYJSONCONFIG_BASE = "PYJSONCONFIG_BASE"

    def __init__(
        self,
        filename=DEFAULT_CONFIG_FILE,
        basepath=None,
        not_exist_ok=True,
        auto_conv=True,
    ):
        if basepath is None:
            basepath = os.environ.setdefault(Config.PYJSONCONFIG_BASE, ".")
        self.basepath = basepath
        self.filename = filename
        self.clear()
        if not not_exist_ok and not self.exists():
            raise Exception("file not exist", self._fullpath())
        self.load()
        if auto_conv:
            self.conv()

    def __repr__(self):
        return f"<Config file={ self._fullpath() } content={ self.data }>"

    def _fullpath(self):
        fullpath = os.path.join(self.basepath, self.filename)
        userpath = os.path.expanduser(fullpath)
        normpath = os.path.normpath(userpath)
        abspath = os.path.abspath(normpath)
        return abspath

    def clear(self):
        self.data = {}

    def conv(self):
        self.data = self._namespace()

    def isconv(self):
        return isinstance(self.data, _cfg_namespace)

    def setdefault(self, key, default_val=None):
        return self.data.setdefault(key, default_val)

    def default(self, o):
        # call the inner default here too ...
        # since it handles both (python and custom class)
        return o.data.default(o)

    def _namespace(self):

        """return a shallow copy of the namespace for this object"""

        if self.isconv():
            return _cfg_namespace(self.data.__dict__)
        return _cfg_namespace(self.data)

    def exists(self):

        """check if file exists and size > 0"""

        fp = self._fullpath()
        return os.path.exists(fp) and os.path.getsize(fp) > 0

    def load(self):
        if self.exists():
            with open(self._fullpath()) as f:
                self.data = json.load(f)
        return self.data

    def savefd(self, fd, indent=4, sort_keys=True):
        conv = None if isinstance(self.data, dict) else self.data.default
        json.dump(self.data, fd, default=conv, indent=indent, sort_keys=sort_keys)

    def save(self, indent=4, sort_keys=True):
        with open(self._fullpath(), "w") as f:
            self.savefd(f, indent, sort_keys)

    def val(self, arr, defval=None, conv=None):
        return self._getconfigval(arr, defval, conv)

    def str(self, arr, defval=""):
        return self._getconfigval(arr, defval, str)

    def bool(self, arr, defval=True):
        conf_bool = lambda t: str(t).lower() == "true"
        return self._getconfigval(arr, defval, conf_bool)

    def int(self, arr, defval=0):
        conf_int = lambda t: int(t)
        return self._getconfigval(arr, defval, conf_int)

    def float(self, arr, defval=0.0):
        conf_float = lambda t: float(t)
        return self._getconfigval(arr, defval, conf_float)

    def __call__(self, evalstr=None):
        if evalstr is None:
            return self.data
        path = evalstr.split(".")
        return path

    def _getconfigval(self, ar, defval=None, conf=None):

        if not isinstance(ar, list):
            raise Exception("arr must be list type")

        arr = []
        arr.extend(ar)
        last = arr.pop()
        e = self.data

        if self.isconv():
            for se in arr:
                if se in e.__dict__:
                    e = e.__dict__[se]
                else:
                    e = e.__dict__.update({se, _cfg_namespace()})

            if last in e.__dict__:
                val = e.__dict__[last]
            else:
                val = defval

            if conf:
                val = conf(val)
            e.__dict__[last] = val
            return val

        else:
            for se in arr:
                e = e.setdefault(se, {})
            val = e.setdefault(last, defval)

            if conf:
                val = conf(val)
            e[last] = val
            return val

    # higher level access and var substitution

    def getexpandvars(self, eval_str):
        """extract vars such as ${user} or ${host.remote_ip} in the eval_str from the config"""
        regex = r"\$\{([a-zA-Z\._]+)\}"
        matches = re.finditer(regex, eval_str, re.MULTILINE)
        vars = []

        for matchNum, match in enumerate(matches, start=1):
            fullmatch = match.group(0)
            selector = match.group(1)
            vars.append((selector, fullmatch))

        return vars

    def expandvars(self, expandvars):
        """expands expandvars from a former call to getexpandvars"""
        vars = []
        for v, s in expandvars:
            val = self.val(self(v))
            vars.append((v, s, val))
        return vars

    def expand(self, eval_str, expandvars=None, recursion_level=3):
        """replace vars in config by config values"""
        while recursion_level > 0:
            recursion_level -= 1
            vars = self.getexpandvars(eval_str)
            if len(vars) == 0:
                break
            exvars = self.expandvars(vars) if expandvars is None else expandvars
            for selector, fullmatch, val in exvars:
                eval_str = eval_str.replace(fullmatch, val)
        return eval_str

    #

    def sanitize(self, addkeywords=[], _dict=None):

        """remove sensitive data from config"""

        keywords = ["user", "pass", "url", "host", "remote", "port"]
        keywords.extend(addkeywords)

        if _dict is None:
            _dict = self.__dict__

        for k, v in _dict.items():
            if isinstance(v, dict):
                self.sanitize(addkeywords=addkeywords, _dict=v)
                continue
            if isinstance(v, _cfg_namespace):
                self.sanitize(addkeywords=addkeywords, _dict=v.__dict__)
                continue
            for kw in keywords:
                if k.lower().find(kw) >= 0:
                    if k.lower().find("default") >= 0:
                        # dont process default settings even when keyword is found
                        continue
                    _dict[k] = f"*** {kw} ***"
