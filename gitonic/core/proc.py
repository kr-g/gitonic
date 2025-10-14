# import os
# import subprocess
# import shlex
# import queue


# class StopSig(object):
#     def __init__(self):
#         self._stop = False

#     def stop(self):
#         self._stop = True

#     def is_stop(self):
#         return self._stop

#     def __repr__(self):
#         return str(self.__dict__)


# class Listener(object):
#     def __init__(self):
#         self.sinks = []

#     def add(self, sink):
#         if sink:
#             self.sinks.extend(sink if type(sink) is list else [sink])
#         return self

#     def call(self, *args, **kwargs):
#         for cb in self.sinks:
#             try:
#                 if cb:
#                     cb(*args, **kwargs)
#             except Exception as ex:
#                 print(ex)


# def run_command(cmd, callback=None, stop_sig=None, rstrip=True, decode=True):

#     cmd = shlex.split(cmd)

#     proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
#                             stderr=subprocess.STDOUT)

#     while proc.returncode is None:

#         if stop_sig and stop_sig.is_stop():
#             proc.kill()
#             break

#         # todo read buffered with timeout
#         rc = proc.stdout.readline()
#         if decode:
#             rc = rc.decode()
#         if rstrip:
#             rc = rc.rstrip()
#         if len(rc) == 0:
#             break

#         if callback:
#             callback(rc)

#     return proc


# class ResultListenerQueue(object):
#     def __init__(self, listener=None, store=True, rstrip=False, decode=False):
#         self.q = queue.Queue()
#         self.sink = Listener().add(listener)
#         self.store = store
#         self.rstrip = rstrip
#         self.decode = decode

#     def add(self, s):
#         if self.rstrip:
#             if type(s) != str:
#                 raise Exception("must be string")
#             s = s.rstrip()
#         if self.decode:
#             if type(s) != bytes:
#                 raise Exception("must be string")
#             s = s.decode()
#         if self.store:
#             self.q.put(s)
#         if self.sink:
#             self.sink.call(s)

#     def get(self):
#         if self.empty() is False:
#             return self.q.get()
#         return None

#     def empty(self):
#         return self.q.empty()

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if self.empty():
#             raise StopIteration
#         return self.get()


# class InterruptableRunner(object):
#     def __init__(self):
#         self._done = False
#         self.rc = None
#         self._stop_sig = None
#         self.config = None

#     def __repr__(self):
#         return str(self.__dict__)

#     def get(self, val, default=None):
#         return val if val != None else default

#     def run_ctx(self, stop_sig=None, config=None):
#         self._stop_sig = stop_sig
#         self.config = config
#         if self.config and "target" in self.config.__dict__:
#             def _run(self):
#                 return self.config.__dict__["target"](self)
#             self.run = _run
#         return self

#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         self._stop_sig = None

#     def start(self):
#         assert self._done == False, "execution finished"
#         self.rc = self.run()
#         self._done = True
#         return self

#     def run(self):
#         """overload this, or use target oaram in config"""
#         pass

#     def stop(self):
#         if type(self._stop_sig) == StopSig:
#             self._stop_sig.stop()
#         else:
#             self._stop_sig = True
#         return self

#     def is_stop(self):
#         if type(self._stop_sig) == StopSig:
#             return self._stop_sig.is_stop()
#         return self._stop_sig

#     def active(self):
#         return self._done


# class SpawnRunner(InterruptableRunner):

#     def run(self):
#         self.proc = run_command(self.config.cmd, self.config.callback,
#                                 self._stop_sig, self.config.rstrip, self.config.decode)
#         return self.proc
