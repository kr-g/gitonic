import os
import threading
from queue import Queue


class Task(threading.Thread):
    def start(self):
        self.qu = Queue()
        self.rc = None
        super().start()

    def _append_rc(self, rc):
        self.qu.put(rc)

    def pop(self):
        try:
            return self.qu.get(block=False)
        except:
            pass

    def popall(self):
        lines = []
        while True:
            l = self.pop()
            if l is None:
                break
            lines.append(l)
        return lines

    def running(self):
        return self.is_alive()

    def failed(self):
        assert not self.running()
        return isinstance(self.rc, Exception)


class Cmd(object):
    def set_command(self, cmd):
        self._cmd = cmd
        self.set_callb()  # todo
        return self

    def set_callb(self, callb=None):
        self._callb = callb
        return self

    def start(self):
        self.run()

    def run(self):
        try:
            with os.popen(self._cmd) as f:
                while True:
                    line = f.readline()
                    if len(line) == 0:
                        break
                    line = line.rstrip()
                    if self._callb:
                        self._callb(line)
            rc = 0
        except Exception as ex:
            rc = ex
        return rc


class CmdTask(Cmd, Task):
    def start(self):
        if self._callb is None:
            self.set_callb(self._append_rc)
        Task.start(self)

    def run(self):
        Task.run(self)
        self.rc = Cmd.run(self)
