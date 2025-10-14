"""
    (c)2021-2025 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""

import sys
import os
import subprocess
import threading
from queue import Queue


def run_proc(
    cmd,
    stdin=None,
    readline=True,
    read_blk=1,
    decode=True,
    combine_stderr=True,
    callb=None,
    donecallb=None,
    stopcallb=None,
    shell=False,
    env=-1,
):
    try:
        rc = None
        proc = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT if combine_stderr else None,
            shell=shell,
            # todo
            env=os.environ if env == -1 else env,
        )

        if proc:
            while True:
                if stopcallb:
                    if stopcallb():
                        break

                recv = None

                if readline:
                    recv = proc.stdout.readline()
                else:
                    recv = proc.stdout.read(read_blk)
                if len(recv) == 0:
                    if donecallb:
                        donecallb()
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


class Runner(object):
    def __init__(self):
        self.idname = ""
        self._init = False
        self._out = []
        self._run = False
        self._rundone = False

        self.configure()

    def set_name(self, name):
        self.idname = name
        return self

    def _append(self, s):
        if self._capture:
            self._out.append(s)
        if self._callb:
            self._callb(s)

    def configure(self, callb=None, stop_callb=None, done_callb=None, capture=True):
        self._callb = callb
        self._stopcb = stop_callb
        self._done_callb = done_callb
        self._capture = capture
        return self

    def start(self):
        pass

    def join(self):
        print("warning, join() in Cmd called", file=sys.stderr)

    def run(self):
        assert self._init
        assert self._rundone is False

        if self._run:
            raise Exception("already done")

        self._run = True

        rc = self._execute()

        self._rundone = True

        return rc

    def _execute(self):
        raise NotImplementedError()

    def result(self):
        return self._out


class Func(Runner):

    def __init__(self):
        Runner.__init__(self)

    def set_func(self, func=None):
        self._func = func

        self._init = True
        return self

    def _execute(self):
        if self._func:
            return self._func(self)
        return 0


class Cmd(Func):

    def __init__(self):
        Func.__init__(self)

    def set_command(self, cmd, decode=True):
        self._cmd = cmd
        self._decode = decode

        return self.set_func(self._func_execute)

    def _func_execute(self, ref):
        rc = run_proc(self._cmd, callb=self._append, donecallb=self._done_callb,
                      stopcallb=self._stopcb, decode=self._decode, shell=True)
        return rc


class Task(threading.Thread):
    def __init__(self):
        super().__init__()

    def start(self):
        self.qu = Queue()
        self.rc = None
        self._stop_req = None

        if self._callb is None:
            self._callb = self._append_rc

        super().start()

    # ??? todo remove ???
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
    # todo end-of remove

    def running(self):
        return self.is_alive()

    # todo
    def failed(self):
        assert not self.running()
        return isinstance(self.rc, Exception)


class FuncTask(Func, Task):
    def __init__(self):
        Func.__init__(self)
        Task.__init__(self)

    def start(self):
        Func.start(self)
        Task.start(self)

    def run(self):
        # ??? todo remove ???
        # Task.run(self)

        # run inside thread and store result
        self.rc = Func.run(self)

    def returnCode(self):
        return self.rc

    def join(self, timeout=None):
        rc = Task.join(self, timeout=timeout)
        return rc


class CmdTask(Cmd, FuncTask):
    def __init__(self):
        FuncTask.__init__(self)
        Cmd.__init__(self)

    def start(self):
        Cmd.start(self)
        FuncTask.start(self)
