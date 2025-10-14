from icons import get_font_icon
import signal

import queue
import sys
# import os

from tkinter import Tk

import tkinter
import tkinter.ttk as ttk

from tkinter import messagebox as tk_messagebox

from threading import Thread

import webbrowser

sys.path.append(".")


#

HEIGHT = 23


def tk_get_icon(name, height=HEIGHT, image_size=(HEIGHT+3, HEIGHT+3), bg="lightgrey", fg="black"):
    return get_font_icon(name, height=height, image_size=image_size, bg=bg, fg=fg)

#


def tk_show_error(title, message):
    tk_messagebox.showerror(title, message)

#


def tk_open_browser_url(url, newtab=True):
    if newtab:
        webbrowser.open_new_tab(url)
    else:
        webbrowser.open_new(url)


#


bg_stop_req = False


def bg_quit():
    global bg_stop_req
    bg_stop_req = True


def tk_shutdown():
    return bg_stop_req


def tk_no_shutdown():
    return not bg_stop_req


#


# class CmdThread(Thread):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.stopped = False

#     def run(self):
#         super.run()

#         self.proc()

#         self.run_done_cleanup()

#     def proc(self):
#         pass

#     def run_done_cleanup(self):
#         pass

#     def stop(self):
#         self.stopped = True
#         super.stop()

#


def tk_get_add_par(nam, defaultval, kwargs):
    if nam in kwargs:
        val = kwargs[nam]
        del kwargs[nam]
        return val
    return defaultval

#


class TkFacade(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._quit_handlers = []

    def add_quit_handler(self, cb):
        self._quit_handlers.append(cb)

    def remove_quit_handler(self, cb):
        self._quit_handlers.remove(cb)

    def quit(self):
        bg_quit()
        for qh in self._quit_handlers:
            try:
                qh()
            except Exception as ex:
                print("shutdown", ex)
        # root.after(10)
        self.destroy()
        super().quit()

#


_root = None

#


def tk_get_root():
    global _root
    if _root is None:
        _root = TkFacade()
    return _root


def ttk_set_sytle(name="clam"):
    tk_get_root()
    s = ttk.Style()
    s.theme_use(name)


def tk_win_minimize():
    print("minimize")
    tk_get_root().iconify()


#

_global_hotkey = set()


def tk_add_hotkey(key, func):
    global _global_hotkey
    if key in _global_hotkey:
        raise Exception("hotkey already registered", key)
    _global_hotkey.add(key)

    assert key.startswith("<")
    assert key.endswith(">")

    def inter(key, func):
        print("key", key)
        func()

    _root.bind(key, lambda x: inter(key, func))


#


# class QCmdThread(CmdThread):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         _root.add_quit_handler(self.stop)

#     def run_done_cleanup(self):
#         super().run_done_cleanup()
#         _root.remove_quit_handler(self.stop)

#


def signal_handler(signal, frame):
    print("SIGINT")
    _root.quit()
    # sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

#


class QuitHandler(object):

    def __init__(self, cb, tkroot=None):
        self.root = tkroot if tkroot else _root
        assert cb
        self.cb = cb

    def __enter__(self):
        self.root.add_quit_handler(self.cb)

    def __exit__(self, exc_type, exc_value, traceback):
        self.root.remove_quit_handler(self.cb)

#


class TkBackgroudTasks(object):
    def __init__(self, root, inq_delay=15):
        self._root = tk_get_root()
        self._root.add_quit_handler(self.stop)

        self._run = True
        self.inq = queue.Queue()
        self.inq_delay = inq_delay
        self._proc_callb()

    def add(self, cb):
        self.inq.put(cb)

    def _proc_callb(self):

        self._afterid = None

        if self._run is False:
            return

        if self.inq.empty() is False:
            cb = self.inq.get()
            try:
                cb()
            except Exception as ex:
                print("catched", ex, file=sys.stderr)

        # trigger next run from root widget
        if self._run:
            self._afterid = self._root.after(self.inq_delay, self._proc_callb)

    def stop(self):
        print("BackgroudTasks stop")
        self._run = False
        if self._afterid:
            self._root.after_cancel(self._afterid)
            self._afterid = None


#

_bg_runner = None


def tk_add_bg_callb(cb, force=False, force_tout=5):
    global _bg_runner

    if tk_shutdown():
        print("tk_add_bg_callb, shutdown in progress", file=sys.stderr)
        return

    if _bg_runner is None:
        _bg_runner = TkBackgroudTasks(root=_root)
    if force is False:
        _bg_runner.add(cb)
    else:
        _root.after(force_tout, cb)


#
