
import sys
import os
import time

import tkinter as tk
import tkinter.ttk as ttk

# todo


#

from tkuicore import tk_get_root, ttk_set_sytle, tk_get_icon, tk_add_hotkey, \
    tk_add_bg_callb, tk_win_minimize, tk_open_browser_url


from tkuiwidg import TNLabel, TNLabelClickUrl, TNButton, TNNotebook

from tkuiview import (T_GITONIC, T_SETTINGS, T_LICENCES, TrackedView, ChangesView,
                      CommitView, LogView, ExtraLogView, PreferencesView, LicenseView)


#
#

root = tk_get_root()


#

ttk_set_sytle()

#


# class Tobj(object):
#     def _setup(self):
#         if self.__dict__.get("_ctx", None) is None:
#             self._ctx = Context()

#     def config(self, *args, **kwargs):
#         Tobj._setup(self)
#         return self

#     def setup(self):
#         Tobj._setup(self)
#         return self

#     def __repr__(self):
#         return self.__class__.__name__ + "(" + str(self._ctx) + ")"


# class TId(Tobj):
#     def config(self, *args, **kwargs):
#         Tobj.config(*args, **kwargs)
#         nam = kwargs.get("id", None)
#         self._ctx.oid = nam if nam else None
#         return self

#     def setup(self):
#         Tobj.setup(self)
#         return self

#


def center_wm_after_startup():
    print(root.winfo_geometry())
    ww = root.winfo_width()
    wh = root.winfo_height()

    wmx, wmy = root.wm_maxsize()

    # center the window
    wx = int(wmx / 2 - ww / 2)
    wy = int(wmy / 2 - wh / 2)

    root.geometry(f"{ww}x{wh}+{wx}+{wy}")


#


#

menubar = tk.Menu(root)
root.config(menu=menubar)

#

file_menu = tk.Menu(menubar, tearoff=False)

settings_icon = tk_get_icon("tune")
file_menu.add_command(
    label='Settings',
    command=lambda: ui_app.main.select_name(T_SETTINGS),
    image=settings_icon, compound=tk.LEFT
)

if False:
    file_menu.add_command(
        label='Keyboard Shortcuts',
        command=root.quit,
    )

about_icon = tk_get_icon("info")
file_menu.add_command(
    label='About',
    command=lambda: ui_app.main.select_name(
        T_LICENCES) and ui_app.pane_licences.ref().select_name(T_GITONIC),
    image=about_icon, compound=tk.LEFT
)

if False:
    file_menu.add_command(
        label='Start <gitk>',
        command=root.quit,
    )
    file_menu.add_command(
        label='Start <git gui>',
        command=root.quit,
    )

exit_icon = tk_get_icon("door_open")
file_menu.add_command(
    label='Exit',
    command=root.quit,
    image=exit_icon, compound=tk.LEFT
)

menubar.add_cascade(
    label="File",
    menu=file_menu
)


#

class LogStore(object):
    def __init__(self):
        self.logs = []

    def cut_to(self, maxcnt):
        if len(self.logs) > maxcnt:
            self.logs = self.logs[len(self.logs)-maxcnt:]

    def add(self, msgs):
        if type(msgs) is list:
            self.logs.extend(msgs)
        else:
            self.logs.append(msgs)


class App(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mouse_busy_cnt = 0

        self._main = TNNotebook(self)
        self._main.pack(expand=True, fill=tk.BOTH)

        self._tracked_tab = ttk.Frame(self._main,)
        self._tracked_tab.pack(expand=True, fill=tk.BOTH)
        self._main.add(self._tracked_tab, text="tracked")

        self._changes_tab = ttk.Frame(self._main,)
        self._changes_tab.pack(expand=True, fill=tk.BOTH)
        self._main.add(self._changes_tab, text="changes")

        self._commit_tab = ttk.Frame(self._main,)
        self._commit_tab.pack(expand=True, fill=tk.BOTH)
        self._main.add(self._commit_tab, text="commit")

        self._log_tab = ttk.Frame(self._main,)
        self._log_tab.pack(expand=True, fill=tk.BOTH)
        self._main.add(self._log_tab, text="log")

        self.logs = {}

        if False:
            self._info_tab = ttk.Frame(self._main,)
            self._info_tab.pack(expand=True, fill=tk.BOTH)
            self._main.add(self._info_tab, text="info")

        self._prefs_tab = ttk.Frame(self._main,)
        self._prefs_tab.pack(expand=True, fill=tk.BOTH)
        self._main.add(self._prefs_tab, text=T_SETTINGS)

        self._license_tab = ttk.Frame(self._main,)
        self._license_tab.pack(expand=True, fill=tk.BOTH)
        self._main.add(self._license_tab, text=T_LICENCES)

        if not False:
            self._logextra_tab = ttk.Frame(self._main,)
            self._logextra_tab.pack(expand=True, fill=tk.BOTH)
            self._main.add(self._logextra_tab, text="expert")

        # todo app

        # self._main.select_name("changes")

        self._init_views()

    def _init_views(self):
        self.pane_tracked = TrackedView(self._tracked_tab, )
        self.pane_tracked.pack(expand=True, fill=tk.BOTH)

        self.pane_changes = ChangesView(self._changes_tab)
        self.pane_changes.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.pane_commit = CommitView(self._commit_tab)
        self.pane_commit.pack(side=tk.LEFT, anchor=tk.NW)

        self.pane_log = LogView(self._log_tab)
        self.pane_log.pack(
            side=tk.LEFT, expand=True, fill=tk.BOTH, padx=7, pady=7)

        self.pane_extralog = ExtraLogView(self._logextra_tab)
        self.pane_extralog.pack(side=tk.LEFT, expand=True,
                                fill=tk.BOTH, padx=7, pady=7)

        self.pane_prefs = PreferencesView(self._prefs_tab)
        self.pane_prefs.pack(side=tk.LEFT, padx=15, anchor=tk.NE)

        self.pane_licences = LicenseView(self._license_tab)
        self.pane_licences.pack(side=tk.LEFT, padx=15, anchor=tk.NE)

    #

    def clean_logs(self, keep):
        for k in self.logs.keys():
            if k not in keep:
                self.logs[k].clear()

    def get_logs(self, repo):
        l = self.logs.setdefault(repo, LogStore())
        return l

    def set_mouse_pointer(self, busy=False):
        self.mouse_busy_cnt += 1 if busy else -1
        img = "watch" if self.mouse_busy_cnt > 0 else ""
        root.config(cursor=img)

    @property
    def main(self):
        return self._main

    def select_tab(self, name="changes"):
        self._main.select_name(name)

    def move_tab(self, x):
        l = len(self.main.tabs())
        pos = self.main.index(ui_app.main.select())
        pos += x
        pos %= l
        self.main.select(pos)
        self.main.focus()

    def setup(self):
        tk_add_hotkey("<F5>", lambda: self.move_tab(-1))
        tk_add_hotkey("<F6>", lambda: self.move_tab(1))

        return self

    def set_title(self, version):
        root.title(f"{T_GITONIC} - {version}")

#


_last_esc = None
_after_id_minify = None


def escesc_handler():
    global _last_esc, _after_id_minify

    if _after_id_minify:
        root.after_cancel(_after_id_minify)
        _after_id_minify = None

    if _last_esc:
        now = time.time_ns()
        if now - _last_esc < 1500 * 1000 * 1000:
            print("double-esc. bye.")
            root.quit()
            return

    _last_esc = time.time_ns()
    _after_id_minify = root.after(500, tk_win_minimize)


tk_add_hotkey("<Escape>", escesc_handler)

root.protocol("WM_DELETE_WINDOW", root.quit)

#

ui_app = App(root,).setup()
ui_app.pack(expand=True, fill=tk.BOTH)

#

creditcardbtn = TNButton(
    root, text="help and sponsor this project (https://github.com/kr-g/gitonic/wiki/Support)", image="credit_card_heart", imagefg="blue")
creditcardbtn.pack(side=tk.TOP, pady=7)

# creditcardbtn.on_click = lambda : tk_open_browser_url("https://www.paypal.com/paypalme/krgo")
creditcardbtn.on_click = lambda: tk_open_browser_url(
    "https://github.com/kr-g/gitonic/wiki/Support")

#

footer = tk.Frame(root)
footer.pack(side=tk.LEFT, anchor=tk.S, expand=True, fill=tk.X, pady=3, padx=3)

prognam = TNLabelClickUrl(
    footer, text=f"{T_GITONIC} - https://github.com/kr-g/gitonic", image="home", compound=tk.LEFT)
prognam.set_url("https://github.com/kr-g/gitonic")
prognam.pack(side=tk.LEFT, expand=False)
prognam.config(cursor="hand2")

sysver = sys.version_info
filler = TNLabel(
    footer, text=f"env: Python {sysver[0]}.{sysver[1]}.{sysver[2]}", image="info", compound=tk.LEFT)
filler.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=15)

#

root.resizable(True, True)
sizegrip = ttk.Sizegrip(footer)
sizegrip.pack(side="right", anchor=tk.SE, expand=False)


#
#
#


if __name__ == "__main__":

    #
    # todo data
    #

    ui_app.pane_tracked.tracked.set_values(
        ["trarepo"+str(x) for x in range(1, 10)])

    #
    repo_items = ["--- all ---", *["repo"+str(x) for x in range(1, 15)]]

    ui_app.pane_changes.repos.set_values(repo_items)

    ui_app.pane_changes.repos.lb.select_clear(0, tk.END)
    ui_app.pane_changes.repos.lb.selection_set(0)

    for i in range(1, 25):
        si = str(i)
        ui_app.pane_changes.add_item(si,
                                     "main"+si,
                                     "test.py"+si,
                                     "-"+si,
                                     "?"+si,
                                     "N"+si)

    #

    ui_app.pane_commit.msg_cb.set_values(['value1', 'value2', 'value3'])

    #

    log_repo_items = ["--- all ---", *
                      ["log repo"+str(x) for x in range(1, 11)]]

    ui_app.pane_log.repos.set_values(log_repo_items)

    ui_app.pane_log.repos.lb.select_clear(0, tk.END)
    ui_app.pane_log.repos.lb.selection_set(0)

    #
    #
    #

    ui_app.set_title("!!!cur-dev!!!")

    root.mainloop()

#

# https://www.pythontutorial.net/tkinter/tkinter-scrollbar/

# https://www.pythontutorial.net/tkinter/tkinter-system-tray/

# https://pystray.readthedocs.io/en/latest/
