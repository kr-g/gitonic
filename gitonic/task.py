"""
    (c)2021 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""

import os
import subprocess
import threading
from queue import Queue


class Task(threading.Thread):
    def start(self):
        self.qu = Queue()
        self.rc = None
        self._stop_req = None
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
        self._stop_req = None
        self.set_callb()  # todo
        return self

    def set_callb(self, callb=None):
        self._callb = callb
        return self

    def start(self):
        self.run()

    def run(self):
        try:
            rc = 0
            proc = subprocess.Popen(
                self._cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
            )
            # with os.popen(self._cmd) as f:
            while True:
                if self._stop_req:
                    return self._stop_req
                # line = f.readline()
                line = proc.stdout.readline().decode()
                if len(line) == 0:
                    break
                line = line.rstrip()
                if self._callb:
                    self._callb(line)
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
