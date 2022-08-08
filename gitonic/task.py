"""
    (c)2021 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""

import os
import subprocess
import threading
from queue import Queue


def run_proc(
    cmd,
    stdin=None,
    readline=True,
    read_blk=5,
    decode=True,
    combine_stderr=True,
    callb=None,
    loopcallb=None,
    shell=False,
):

    try:
        rc = None
        proc = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT if combine_stderr else None,
            shell=shell,
        )

        if proc:
            while True:

                if loopcallb:
                    if loopcallb(proc):
                        break

                recv = None

                if readline:
                    recv = proc.stdout.readline()
                else:
                    recv = proc.stdout.read(read_blk)
                if len(recv) == 0:
                    break
                if decode:
                    recv = recv.decode()
                if callb:
                    callb(recv)

            proc.wait()

            if proc.returncode == 0:
                return
            return proc.returncode

        else:
            rc = 1

    except Exception as ex:
        rc = ex

    return rc


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
        pass

    def _loopcb(self, p):
        if self._stop_req:
            return self._stop_req

    def run(self):
        rc = run_proc(self._cmd, callb=self._callb, loopcallb=self._loopcb, shell=True)
        return rc


class CmdTask(Cmd, Task):
    def start(self):
        if self._callb is None:
            self.set_callb(self._append_rc)
        Task.start(self)
        Cmd.start(self)

    def run(self):
        Task.run(self)
        self.rc = Cmd.run(self)
