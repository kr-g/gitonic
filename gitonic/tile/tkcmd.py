"""
    (c)2021 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""


class TkCmd(object):
    class Options(object):
        def __init__(self, opts):
            self.__dict__.update(opts)

    def start(
        self,
        parent,
        command=None,
        tout=1000,
        detached=False,
        info=None,
        **opts,
    ):
        self.parent = parent
        self.tout = tout
        self.rc = None
        self._stop = None
        self._cmd = command
        self.opts = TkCmd.Options(opts) if opts and type(opts) == dict else opts
        self._detached = detached
        self._info = info
        self._disp(True)
        return self

    def _disp(self, schedule=False):
        if not self._detached:
            get_tk_cmd_manager().remove(self)
        if schedule:
            if not self._detached:
                get_tk_cmd_manager().add(self, self._info)
            self.parent.after(self.tout, self._disp)
            return
        if self._stop:
            self.rc = self._stop
            return
        self.rc = self.run()
        if self.rc is None:
            self._disp(True)

    def run(self):
        """overload this, or use command paramter in start"""
        if self._cmd:
            return self._cmd(self)
        return 0


class TkCmdManager(object):
    def __init__(self):
        self._pending = {}

    def add(self, tkcmd, info=None):
        if info is None:
            info = f"tkcmd {hex(id(tkcmd))}"
            tkcmd._info = info
        self._pending[tkcmd] = info

    def remove(self, tkcmd):
        try:
            del self._pending[tkcmd]
        except:
            pass

    def clear(self):
        self._pending.clear()


def get_tk_cmd_manager():
    global _tk_man
    try:
        if _tk_man is None:
            raise Exception("not found")
    except:
        _tk_man = TkCmdManager()
    return _tk_man
