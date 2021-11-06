from . import VERSION

import os
import time
import json
import webbrowser

from pyjsoncfg import Config

import tkinter
from tkinter import Tk

from .tile import *
from .file import FileStat
from .sysutil import open_file_explorer

from .gitutil import set_git_exe, GIT, GitWorkspace, git_diff, git_difftool
from .gitutil import run_black, git_add, git_add_undo, git_commit
from .gitutil import git_pull, git_push, git_push_tags, git_push_all


# global

url_homepage = "https://github.com/kr-g/gitonic"
url_sponsor = "https://github.com/sponsors/kr-g"

# configuration

fconfigdir = FileStat("~").join([".gitonic"])
frepo = FileStat("~/repo")
max_history = 1000
max_commit = 15
git_exe = GIT
follow = True
auto_switch = True
push_tags = False
min_commit_length = 5


def set_config():
    global frepo
    frepo = FileStat(config().workspace)
    global max_history
    max_history = config().max_history
    global max_commit
    max_commit = config().max_commit

    global git_exe
    git_exe = config().git_exe
    set_git_exe(git_exe)

    global follow
    follow = bool(config().follow)
    global auto_switch
    auto_switch = bool(config().auto_switch)
    global push_tags
    push_tags = bool(config().push_tags)

    global min_commit_length
    min_commit_length = config().min_commit_length


def read_config():
    global config
    fconfig = FileStat(fconfigdir.name).join(["config.json"]).name
    config = Config(filename=fconfig)
    config().setdefault("workspace", frepo.name)
    config().setdefault("max_history", max_history)
    config().setdefault("max_commit", max_commit)
    config().setdefault("git_exe", GIT)
    config().setdefault("follow", follow)
    config().setdefault("auto_switch", auto_switch)
    config().setdefault("push_tags", push_tags)
    config().setdefault("min_commit_length", min_commit_length)

    set_config()


def write_config():
    print("write_config")
    config().workspace = gt("workspace").get_val()
    config().max_history = gt("max_history").get_val()
    config().max_commit = gt("max_commit").get_val()
    config().git_exe = gt("git_exe").get_val()
    config().follow = bool(int(gt("follow").get_val()))
    config().auto_switch = bool(int(gt("auto_switch").get_val()))
    config().push_tags = bool(int(gt("push_tags").get_val()))
    config().min_commit_length = gt("min_commit_length").get_val()

    config.save()
    set_config()


#


main = TileRows(
    source=[
        TileTab(
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
                                on_select=lambda x: write_config(),
                            ),
                            TileLabel(
                                caption="refresh tracked git's on the next tab manually"
                            ),
                            TileLabel(caption=""),
                            TileEntryInt(
                                caption="minimum commit text length",
                                idn="min_commit_length",
                                value=min_commit_length,
                                on_change=lambda o, n: write_config(),
                            ),
                            TileEntryInt(
                                caption="max records in log history",
                                idn="max_history",
                                value=max_history,
                                on_change=lambda o, n: write_config(),
                            ),
                            TileEntryInt(
                                caption="max records in commit history",
                                idn="max_commit",
                                value=max_commit,
                                on_change=lambda o, n: write_config(),
                            ),
                            TileEntry(
                                caption="git executable",
                                idn="git_exe",
                                value=GIT,
                                on_change=lambda o, n: write_config(),
                            ),
                            TileLabelButton(
                                caption="open gitonic config folder",
                                on_click=lambda x: open_file_explorer(fconfigdir.name),
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
                                    ("unstaged", None),
                                    ("staged", None),
                                    ("type", None),
                                ],
                                header_width=(150, 250, 100, 100, 100),
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
                            TileEntryCombo(
                                caption="message:",
                                idn="commit_short",
                                width=50,
                                on_select=lambda x, v: on_sel_commit(x),
                            ),
                            TileEntryText(
                                caption="", idn="commit_long", width=80, height=10
                            ),
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
                                    TileLabelButton(
                                        caption="tracked git's",
                                        commandtext="push",
                                        command=lambda: on_push_tracked(),
                                    ),
                                    TileCheckbutton(
                                        caption="push tags",
                                        idn="push_tags",
                                        on_click=lambda x: write_config(),
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
                                caption="",
                                idn="log",
                                height=20,
                                width=80,
                                readonly=True,
                            ),
                            TileCols(
                                source=[
                                    TileLabelButton(
                                        caption="",
                                        commandtext="clear",
                                        command=lambda: on_log_clr(),
                                    ),
                                    TileCheckbutton(
                                        caption="follow log",
                                        idn="follow",
                                        on_click=lambda x: write_config(),
                                    ),
                                    TileCheckbutton(
                                        caption="auto switch log",
                                        idn="auto_switch",
                                        on_click=lambda x: write_config(),
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
                # ("about", Tile()),
            ],
        ),
        TileCols(
            source=[
                TileLabelClick(
                    caption=f"gitonic - {url_homepage}",
                    on_click=lambda x: open_homepage(),
                ),
                TileLabel(
                    caption=f"version: {VERSION}",
                ),
                TileLabelClick(
                    caption=f"DONATE to gitonic - {url_sponsor}",
                    on_click=lambda x: open_sponsor_page(),
                ),
            ]
        ),
    ]
)


# gui handling


def open_homepage():
    webbrowser.get().open(url_homepage, new=0)


def open_sponsor_page():
    webbrowser.get().open(url_sponsor, new=0)


def on_sel_all_gits():
    print("on_sel_all_gits")
    gt("gits").set_selection(-1)
    set_tracked_gits()


def on_unsel_all_gits():
    print("on_sel_all_gits")
    gt("gits").clr_selection()
    set_tracked_gits()


def on_cmd_diff(info, diff_):
    print(info)
    sel = gt("changes").get_selection_values()
    for rec in sel:
        if rec["type"] == "file":
            pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
            git = gws.find(pg)[0]
            rc = diff_(git.path, rec["file"])
            print(f"--- {git}")
            [print(x) for x in rc]
            do_log_time(info)
            do_logs(rc)


def on_diff():
    on_cmd_diff("on_diff", git_diff)


def on_difftool():
    on_cmd_diff("on_difftool", git_difftool)


def on_log_clr():
    print("on_log_clr")
    gt("log").clr()


def do_log_max_history():
    print("do_log_max_history")
    log = gt("log")
    cnt = log.get_line_count()
    if cnt >= max_history:
        to_del = float(cnt - max_history)
        log.remove_lines(last=to_del)


def on_follow_log():
    if follow:
        gt("log").gotoline()
    do_log_max_history()


def do_log_show(ignore_switch=False):
    if not ignore_switch and auto_switch:
        gt("maintabs").select("tab_log")


def do_log_time(x, ignore_switch=False):
    print("do_log_time", x)
    do_log_show(ignore_switch)
    log = gt("log")
    ts = time.asctime(time.localtime(time.time()))
    log.append(f"\n\n\n--- {x} --- {ts}")
    on_follow_log()


def do_log(x=""):
    print("do_log", x)
    gt("log").append(x)
    on_follow_log()


def do_logs(x):
    print("do_logs", x)
    gt("log").extend(x)
    on_follow_log()


tracked = FileStat(fconfigdir.name).join(["tracked.json"])
tracked.makedirs()


def tracked_write():
    with open(tracked.name, "w") as f:
        f.write(json.dumps(tracked_gits, indent=4))


def tracked_read():
    try:
        with open(
            tracked.name,
        ) as f:
            cont = f.read()
            global tracked_gits
            tracked_gits = json.loads(cont)
            print(tracked, "->", tracked_gits)
            sel_tracked()
    except Exception as ex:
        print(ex)


def sel_tracked():
    gt("gits").set_selection(tracked_gits)


def on_gits_cmd(info, selcmd_, gits, ignore_switch=False, update_change=False):
    do_log_time(info, ignore_switch)
    for rec in gits:
        pg = FileStat(gws.base_repo_dir.name).join([rec["git"]]).name
        git = gws.find(pg)[0]
        rc = selcmd_(git.path, [rec["file"]])
        print(f"--- {git}")
        [print(x) for x in rc]
        do_logs(rc)
    if update_change:
        set_changes()


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


def on_sel_cmd(info, selcmd_, ignore_switch=False, update_change=False):
    print(info)
    gits = gt("changes").get_selection_values()
    on_gits_cmd(
        info, selcmd_, gits, ignore_switch=ignore_switch, update_change=update_change
    )


def on_add():
    on_sel_cmd("on_add", git_add, True, True)


def on_add_undo():
    on_sel_cmd("on_add", git_add_undo, True, True)


fcommit = FileStat(fconfigdir.name).join(["commit.json"])
commit_history = []


def read_commit():
    global commit_history
    try:
        with open(fcommit.name) as f:
            cont = f.read()
            commit_history = json.loads(cont)
    except Exception as ex:
        print(ex)
    set_commits()


def write_commit():
    try:
        with open(fcommit.name, "w") as f:
            cont = json.dumps(commit_history, indent=4)
            f.write(cont)
    except Exception as ex:
        print(ex)


def add_commit_history(short, long):
    global commit_history
    commit = {"short": short, "long": long}
    try:
        commit_history.remove(commit)
    except:
        pass
    commit_history.insert(0, commit)
    if len(commit_history) > max_commit:
        commit_history = commit_history[0:max_commit]
    write_commit()
    set_commits()


def set_commits():
    global commit_history
    commits = gt("commit_short")
    vals = list(map(lambda x: x["short"], commit_history))
    print("*********vals", vals)
    commits.set_values(vals)
    if len(vals) > 0:
        commits.set_index(0)
        gt("commit_long").set_val(commit_history[0]["long"])


def on_sel_commit(idx):
    print(idx)
    # gt("commit_short").set_val(commit_history[idx]["short"])
    gt("commit_long").set_val(commit_history[idx]["long"])


def on_clr_commit():
    gt("commit_short").clr()
    gt("commit_long").clr()


def on_commit():
    print("on_commit")
    head = gt("commit_short").get_val().strip()
    body = gt("commit_long").get_val().strip()

    if len(head) < min_commit_length or len(head) > 50:
        tkinter.messagebox.showerror(
            "error",
            f"length: {min_commit_length} >= message < 50\ncurrent: {len(head)}",
        )
        return

    message = head
    if len(body) > 0:
        message += "\n" * 2 + body

    add_commit_history(head, body)

    for gnam in tracked_gits:
        try:
            print("use", gnam)
            git = gws.find(gnam)[0]
            do_log_time(f"commit: {git.path} '{message}'")
            if git.has_staged():
                rc = git_commit(git.path, message)
                print(f"--- {git}")
                [print(x) for x in rc]
                do_logs(rc)
                do_log("commited staged files")
            else:
                do_log("nothing staged")

        except Exception as ex:
            print(ex)

    set_changes()


def on_cmd_push(info, push_, gits):
    print(info)
    sel = gt("changes").get_selection_values()
    do_log_time(info)
    for pg in gits:
        git = gws.find(pg)[0]
        rc = push_(
            git.path,
        )
        [print(x) for x in rc]
        do_log()
        do_log(f"--- push: {git}")
        do_logs(rc)
        if push_tags:
            rc = git_push_tags(git.path)
            [print(x) for x in rc]
            do_log()
            do_log(f"--- push tags: {git}")
            do_logs(rc)


def on_push_tracked():
    print("on_push_tracked")
    cmd_ = git_push
    on_cmd_push(
        "on_push_tracked",
        cmd_,
        tracked_gits,
    )


def on_push_all_workspace():
    print("on_push_all_workspace")
    cmd_ = git_push
    on_cmd_push(
        "on_push_all_workspace",
        cmd_,
        sorted(gws.gits.keys()),
    )


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


def set_changes():
    print("set_changes")
    global changes
    changes = []

    gits = list(map(lambda x: (x, gws.find(x)), tracked_gits))
    print(gits)

    for path_git in gits:
        path, git = path_git

        print(path, git)

        fs = FileStat(path, prefetch=True)
        if not fs.exists():
            continue
        gitnam = fs.basename()

        git = git[0]
        git.refresh_status()

        if len(git.status) > 0:
            for stat in git.status:
                fs = git.stat(stat)
                fs_ex = fs.exists()
                gst = {
                    "git": gitnam,
                    "file": stat.file,
                    "unstaged": stat.mode,
                    "staged": stat.staged,
                    "type": ("file" if fs.is_file() else "dir")
                    if fs_ex
                    else "---deleted---",
                }
                changes.append(gst)
    gt("changes").set_values(changes)


def startup_gui():
    read_config()
    read_commit()
    set_workspace(True)

    if len(changes) > 0:
        gt("maintabs").select("tab_changes")

    gt("follow").set_val(follow)
    gt("auto_switch").set_val(auto_switch)
    gt("push_tags").set_val(push_tags)
