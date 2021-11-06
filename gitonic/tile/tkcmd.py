class TkCmd(object):
    class Options(object):
        def __init__(self, opts):
            self.__dict__.update(opts)

    def start(
        self,
        parent,
        command=None,
        tout=1000,
        **opts,
    ):
        self.parent = parent
        self.tout = tout
        self.rc = None
        self._stop = None
        self._cmd = command
        self.opts = TkCmd.Options(opts) if opts and type(opts) == dict else opts
        self._disp(True)
        return self

    def _disp(self, schedule=False):
        if schedule:
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
