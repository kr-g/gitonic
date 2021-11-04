VERSION = "v0.0.1-a"

import os
import time
import json

from tile import *

import tkinter
from tkinter import Tk

from file import FileStat
from gitutil import GitWorkspace, git_diff, git_difftool
from gitutil import run_black, git_add, git_add_undo, git_commit
from gitutil import git_pull, git_push, git_push_tags, git_push_all

#

frepo = FileStat("~/repo")

tk_root = Tk()

mainframe = Tile(tk_root=tk_root, idn="mainframe")


main = TileTab(
    idn="maintabs",
    source=[
        (
            "settings",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileDirectorySelect(
                        caption="select workspace",
                        commandtext="...",
                        idn="workspace",
                        path=frepo.name,
                    ),
                ]
            ),
        ),
        (
            "tracked git's",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntryListbox(
                        caption="",
                        idn="gits",
                        max_show=15,
                        width=40,
                        select_many=True,
                        map_value=lambda x: os.path.basename(x),
                        on_sel=lambda x: set_tracked_gits(),
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="workspace",
                                commandtext="refresh",
                                command=lambda: set_workspace(),
                            ),
                            TileLabelButton(
                                caption="all",
                                commandtext="select",
                                command=lambda: on_sel_all_gits(),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="un-select",
                                command=lambda: on_unsel_all_gits(),
                            ),
                        ]
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="pull",
                                commandtext="selected",
                                command=lambda: on_pull_tracked(),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="all",
                                command=lambda: pull_all_workspace(),
                            ),
                        ]
                    ),
                ]
            ),
        ),
        (
            "changes",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileTreeView(
                        caption="",
                        idn="changes",
                        header=[
                            ("git", None),
                            ("file", None),
                            ("state", "mode / staged"),
                            ("type", None),
                        ],
                    ),
                    TileLabelButton(
                        caption="",
                        commandtext="refresh",
                        command=lambda: set_changes(),
                    ),
                    TileCols(
                        source=[
                            # TileLabelButton(
                            #    caption="selected",
                            #    commandtext="run black",
                            #    command=lambda: on_black(),
                            # ),
                            TileLabelButton(
                                caption="selected",
                                commandtext="add",
                                command=lambda: on_add(),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="unstage",
                                command=lambda: on_add_undo(),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="diff",
                                command=lambda: on_diff(),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="difftool",
                                command=lambda: on_difftool(),
                            ),
                            TileLabelButton(
                                caption="all",
                                commandtext="select",
                                command=lambda: gt("changes").set_selection(-1),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="unselect",
                                command=lambda: gt("changes").clr_selection(),
                            ),
                        ]
                    ),
                ]
            ),
        ),
        (
            "commit",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntry(caption="message:", idn="commit_short", width=50),
                    TileEntryText(caption="", idn="commit_long", width=80, height=10),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="",
                                commandtext="commit",
                                command=lambda: on_commit(),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="clear",
                                command=lambda: on_clr_commit(),
                            ),
                        ]
                    ),
                ]
            ),
        ),
        #         (
        #             "tag",
        #             TileRows(
        #                 source=[
        #                     TileLabel(caption=""),
        #                     TileEntryButton(
        #                         caption="new tag name",
        #                         commandtext="tag",
        #                         idn="tag_workspace",
        #                     ),
        #                 ]
        #             ),
        #         ),
        (
            "log",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntryText(
                        caption="", idn="log", height=20, width=80, readonly=True
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="",
                                commandtext="clear",
                                command=lambda: on_log_clr(),
                            ),
                            TileCheckbutton(caption="follow log", idn="follow"),
                            TileCheckbutton(
                                caption="auto switch log", idn="auto_switch"
                            ),
                        ]
                    ),
                ]
            ),
        ),
    ],
)


def quit_all(frame):
    def quit():
        print("quit_all")
        # removes all, including threads
        # sys.exit()
        # soft, state remains
        # download_stop()
        frame.quit()

    return quit


def minimize():
    print("minimize")
    tk_root.iconify()


url_homepage = "https://github.com/kr-g/pygitonic"


def open_homepage():
    import webbrowser

    webbrowser.get().open(url_homepage, new=0)


main_content = TileRows(
    source=[
        TileCols(
            source=[
                TileLabelButton(
                    caption="close app", commandtext="bye", command=quit_all(mainframe)
                ),
                TileLabelButton(caption="", commandtext="minimize", command=minimize),
            ]
        ),
        main,
        TileCols(
            source=[
                TileLabelClick(
                    caption=f"gitonic - {url_homepage}",
                    on_click=lambda x: open_homepage(),
                ),
                TileLabel(
                    caption=f"version: {VERSION}",
                ),
            ]
        ),
    ]
)

mainframe.tk.protocol("WM_DELETE_WINDOW", quit_all(mainframe))
mainframe.tk.bind("<Escape>", lambda e: minimize())

mainframe.title("gitonic")
mainframe.resize_grip()

mainframe.add(main_content)
mainframe.layout()

# gui handling


def on_sel_all_gits():
    print("on_sel_all_gits")
    gt("gits").set_selection(-1)
    set_tracked_gits()


def on_unsel_all_gits():
    print("on_sel_all_gits")
    gt("gits").clr_selection()
    set_tracked_gits()


def on_diff():
    print("on_diff")
    sel = gt("changes").get_selection_values()
    for rec in sel:
        if rec["type"] == "file":
            pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
            git = gws.find(pg)[0]
            rc = git_diff(git.path, rec["file"])
            print(f"--- {git}")
            [print(x) for x in rc]
            do_log_time("on_diff")
            do_logs(rc)


def on_difftool():
    print("on_difftool")
    sel = gt("changes").get_selection_values()
    for rec in sel:
        if rec["type"] == "file":
            pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
            git = gws.find(pg)[0]
            rc = git_difftool(git.path, rec["file"])
            print(f"--- {git}")
            [print(x) for x in rc]
            do_log_time("on_difftool")
            do_logs(rc)


def on_log_clr():
    print("on_log_clr")
    gt("log").clr()


def on_follow_log():
    if int(gt("follow").get_val()) > 0:
        gt("log").gotoline()


def do_log_show(ignore_switch=False):
    if not ignore_switch and int(gt("auto_switch").get_val()) > 0:
        gt("maintabs").select("tab_log")


def do_log_time(x, ignore_switch=False):
    print("do_log_time", x)
    do_log_show(ignore_switch)
    log = gt("log")
    ts = time.asctime(time.localtime(time.time()))
    log.append(f"\n\n\n--- {x} --- {ts}")
    on_follow_log()


def do_log(x):
    print("do_log", x)
    gt("log").append(x)
    on_follow_log()


def do_logs(x):
    print("do_logs", x)
    gt("log").extend(x)
    on_follow_log()


tracked = FileStat(FileStat.get_tempdir()).join(["gitonic", "tracked.json"])
tracked.makedirs()


def tracked_write():
    with open(tracked.name, "w") as f:
        f.write(json.dumps(tracked_gits))


def tracked_read():
    try:
        with open(
            tracked.name,
        ) as f:
            cont = f.read()
            global tracked_gits
            tracked_gits = json.loads(cont)
            sel_tracked()
    except Exception as ex:
        print(ex)


def sel_tracked():
    gt("gits").set_selection(tracked_gits)


def pull_gits(gits):
    print("on_pull_gits")
    for gnam in gits:
        try:
            git = gws.find(gnam)[0]
            rc = git_pull(git.path)
            print(f"--- {git}")
            [print(x) for x in rc]
            do_log_time(f"pull: {git.path}")
            do_logs(rc)
        except Exception as ex:
            print(ex)
    set_changes()


def on_pull_tracked():
    pull_gits(tracked_gits)


def pull_all_workspace():
    pull_gits(sorted(gws.gits.keys()))


def on_black():
    print("on_black")
    sel = gt("changes").get_selection_values()
    for rec in sel:
        pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
        git = gws.find(pg)[0]
        rc = run_black(git.path, [rec["file"]])
        print(f"--- {git}")
        [print(x) for x in rc]
        do_log_time("on_black", True)
        do_logs(rc)
    # set_changes()


def on_add():
    print("on_add")
    sel = gt("changes").get_selection_values()
    for rec in sel:
        pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
        git = gws.find(pg)[0]
        rc = git_add(git.path, [rec["file"]])
        print(f"--- {git}")
        [print(x) for x in rc]
        do_log_time("on_add", True)
        do_logs(rc)
    set_changes()


def on_add_undo():
    print("on_add_undo")
    sel = gt("changes").get_selection_values()
    for rec in sel:
        pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
        git = gws.find(pg)[0]
        rc = git_add_undo(git.path, [rec["file"]])
        print(f"--- {git}")
        [print(x) for x in rc]
        do_log_time("on_add_undo", True)
        do_logs(rc)
    set_changes()


def on_clr_commit():
    gt("commit_short").clr()
    gt("commit_long").clr()


def on_commit():
    print("on_commit")
    head = gt("commit_short").get_val().strip()
    body = gt("commit_long").get_val().strip()

    if len(head) < 10 or len(head) > 50:
        tkinter.messagebox.showerror(
            "error",
            f"length: 10 > message < 50\ncurrent: {len(head)}",
        )
        return

    message = head
    if len(body) > 0:
        message += "\n" * 2 + body

    for gnam in tracked_gits:
        try:
            print("use", gnam)
            git = gws.find(gnam)[0]
            rc = git_commit(git.path, message)
            print(f"--- {git}")
            [print(x) for x in rc]
            do_log_time(f"commit: {git.path} '{message}'")
            do_logs(rc)
        except Exception as ex:
            print(ex)

    set_changes()


# init


def set_workspace(update=True):
    print("refresh_workspace")
    global gws
    gws = GitWorkspace(frepo.name)
    gws.refresh()
    gt("gits").set_values(sorted(gws.gits.keys()))
    print("gws", gws)
    # gws.refresh_status()
    if update:
        tracked_read()
        set_tracked_gits()


def set_tracked_gits(update=True):
    print("set_tracked_gits")
    global tracked_gits
    tracked_gits = gt("gits").get_selection_values()
    tracked_gits = list(map(lambda x: x[1], tracked_gits))
    print("tracked_gits", tracked_gits)
    tracked_write()
    if update:
        set_changes()


set_workspace(False)
tracked_read()

# set_tracked_gits(False)


def set_changes():
    print("set_changes")
    global changes
    changes = []

    gits = list(map(lambda x: (x, gws.find(x)[0]), tracked_gits))
    print(gits)

    for path, git in gits:
        rnam = FileStat(path).basename()
        git.refresh_status()
        if len(git.status) > 0:
            for stat in git.status:
                fs = git.stat(stat)
                gst = {
                    "git": rnam,
                    "file": stat.file,
                    "state": stat.mode + " / " + stat.staged,
                    "type": ("file" if fs.is_file() else "dir"),
                }
                changes.append(gst)
    gt("changes").set_values(changes)


set_changes()
if len(changes) > 0:
    gt("maintabs").select("tab_changes")

gt("follow").set_val(1)
gt("auto_switch").set_val(1)

# end-of init

print(tk_root.geometry())
print(tk_root.winfo_reqwidth(), tk_root.winfo_reqheight())

mainframe.mainloop()
