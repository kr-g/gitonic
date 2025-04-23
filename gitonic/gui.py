

from .const import VERSION

import os
import sys
import time
import json
import webbrowser
import fnmatch

from .pyjsoncfg import Config

import tkinter
from tkinter import Tk

from .icons import get_icon

from .tile import *
from .file import FileStat, PushDir
from .sysutil import open_file_explorer

from .gitutil import set_git_exe, GIT, GitWorkspace, git_diff, git_difftool
from .gitutil import run_black, git_add, git_add_undo, git_commit
from .gitutil import git_fetch, git_pull, git_push, git_push_tags, git_push_all

from .gitutil import with_cmd
from .task import run_proc


# global

url_homepage = "https://github.com/kr-g/gitonic"
# url_sponsor = "https://github.com/sponsors/kr-g"

# configuration

fconfigdir = FileStat("~").join([".gitonic"])
frepo = FileStat("~/repo")
max_history = 1000
max_commit = 15
git_exe = GIT
follow = True
auto_switch = True
push_tags = False
show_changes = False
clear_after_commit = False
min_commit_length = 5
dev_mode = False
dev_follow = True
dev_follow_max = 10000

#

ICO_TRASH = "trash"
ICO_FOLDER_OPEN = "folder-open"
ICO_REFRESH = "rotate"
ICO_SEL_ALL = "check-double"
ICO_CLR_ALL = "xmark"
ICO_CLR = "xmark"
ICO_PULL = "angle-down"
ICO_PULL_ALL = "angles-down"
ICO_FETCH = "angle-down"
ICO_FETCH_ALL = "angles-down"
ICO_FILE_ADD = "file-circle-plus"
ICO_FILE_SUB = "file-circle-minus"
ICO_FILE_DIFF = "file-waveform"
ICO_FILE_DIFFTOOL = "code-compare"
ICO_FILE_FORMATSOURCE = "indent"

#


def dgb_pr(*s):
    if not True:
        print(s)
    if dev_mode:
        gt("expert_log").append("\t".join([str(x) for x in s]))
        on_follow_expert()


def do_expert_max_history():
    log = gt("expert_log")
    cnt = log.get_line_count()
    if cnt >= dev_follow_max:
        to_del = float(cnt - dev_follow_max)
        log.remove_lines(last=to_del)


def on_follow_expert():
    if dev_follow:
        gt("expert_log").gotoline()
    do_expert_max_history()


def on_expert_clr():
    el = gt("expert_log")
    if el:
        el.clr()
    dgb_pr("on_expert_clr")


def set_config():
    global config

    dgb_pr("set-config", config.__dict__)

    global frepo
    frepo = config().workspace
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
    global show_changes
    show_changes = bool(config().show_changes)

    global min_commit_length
    min_commit_length = config().min_commit_length

    global clear_after_commit
    clear_after_commit = bool(config().clear_after_commit)

    global dev_mode
    dev_mode = config().dev_mode
    global dev_follow
    dev_follow = config().dev_follow
    global dev_follow_max
    dev_follow_max = config().dev_follow_max


def read_config(autocfg=True):
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
    config().setdefault("show_changes", show_changes)
    config().setdefault("min_commit_length", min_commit_length)
    config().setdefault("clear_after_commit", clear_after_commit)
    config().setdefault("dev_mode", dev_mode)
    config().setdefault("dev_follow", dev_follow)
    config().setdefault("dev_follow_max", dev_follow_max)

    if autocfg:
        set_config()


def write_config():
    dgb_pr("write_config")
    global config
    config().workspace = gt("workspace").get_val()
    config().max_history = int(gt("max_history").get_val())
    config().max_commit = int(gt("max_commit").get_val())
    config().git_exe = gt("git_exe").get_val()
    config().follow = bool(int(gt("follow").get_val()))
    config().auto_switch = bool(int(gt("auto_switch").get_val()))
    config().push_tags = bool(int(gt("push_tags").get_val()))
    config().show_changes = bool(int(gt("show_changes").get_val()))
    config().clear_after_commit = bool(int(gt("clear_after_commit").get_val()))
    config().min_commit_length = int(gt("min_commit_length").get_val())
    config().dev_mode = bool(int(gt("dev_mode").get_val()))
    if dev_mode:
        config().dev_follow = bool(int(gt("dev_follow").get_val()))
        config().dev_follow_max = int(gt("dev_follow_max").get_val())

    dgb_pr("write-config", config.__dict__)

    config.save()
    set_config()


#

PREFS_CAP_W = 27
PREFS_ENTRY_W = 7


def trackgit_name(nam):
    userhome = os.path.expanduser("~")
    if nam.startswith(userhome + os.sep):
        nam = nam.replace(userhome, "~")
    return nam


def update_workspace():
    write_config()
    set_workspace()


def get_main():
    read_config()

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
                                TileEntry(
                                    caption="workspace folders",
                                    # commandtext="...",
                                    # icon=get_icon(ICO_FOLDER_OPEN),
                                    width=60,
                                    idn="workspace",
                                    value=frepo,
                                    on_change=lambda o, n: update_workspace(),
                                ),
                                TileLabel(
                                    caption="use ';' as separator for multiple workspaces"
                                ),
                                TileLabel(caption=""),
                                TileEntryInt(
                                    caption="minimum commit text length",
                                    caption_width=PREFS_CAP_W,
                                    width=PREFS_ENTRY_W,
                                    idn="min_commit_length",
                                    value=min_commit_length,
                                    on_change=lambda o, n: write_config(),
                                ),
                                TileEntryInt(
                                    caption="max records in log history",
                                    caption_width=PREFS_CAP_W,
                                    width=PREFS_ENTRY_W,
                                    idn="max_history",
                                    value=max_history,
                                    on_change=lambda o, n: write_config(),
                                ),
                                TileEntryInt(
                                    caption="max records in commit history",
                                    caption_width=PREFS_CAP_W,
                                    width=PREFS_ENTRY_W,
                                    idn="max_commit",
                                    value=max_commit,
                                    on_change=lambda o, n: write_config(),
                                ),
                                TileEntry(
                                    caption="git executable",
                                    caption_width=PREFS_CAP_W,
                                    idn="git_exe",
                                    value=GIT,
                                    on_change=lambda o, n: write_config(),
                                ),
                                TileCheckbutton(
                                    caption="always show changes tab on startup",
                                    idn="show_changes",
                                    on_click=lambda x: write_config(),
                                ),
                                TileCheckbutton(
                                    caption="expert mode. shows debug logging in extra tab (requires restart of gitonic)",
                                    idn="dev_mode",
                                    on_click=lambda x: write_config(),
                                ),
                                TileEntryInt(
                                    caption="max records in expert log history",
                                    caption_width=PREFS_CAP_W,
                                    width=PREFS_ENTRY_W,
                                    idn="dev_follow_max",
                                    value=dev_follow_max,
                                    on_change=lambda o, n: write_config(),
                                ),
                                #
                                TileLabelButton(
                                    caption="open gitonic config folder",
                                    icon=get_icon(ICO_FOLDER_OPEN),
                                    on_click=lambda x: open_file_explorer(
                                        fconfigdir.name
                                    ),
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
                                    map_value=lambda x: trackgit_name(
                                        x),  # os.path.basename(x),
                                    on_sel=lambda x: set_tracked_gits(),
                                ),
                                TileCols(
                                    source=[
                                        TileLabelButton(
                                            caption="workspace",
                                            commandtext="refresh",
                                            icon=get_icon(ICO_REFRESH),
                                            command=lambda: set_workspace(),
                                        ),
                                        TileLabelButton(
                                            caption="all",
                                            commandtext="select",
                                            icon=get_icon(ICO_SEL_ALL),
                                            command=lambda: on_sel_all_gits(),
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="un-select",
                                            icon=get_icon(ICO_CLR_ALL),
                                            command=lambda: on_unsel_all_gits(),
                                        ),
                                    ]
                                ),
                                TileCols(
                                    source=[
                                        TileLabelButton(
                                            caption="pull",
                                            commandtext="selected",
                                            icon=get_icon(ICO_PULL),
                                            command=lambda: on_pull_tracked(),
                                            hotkey="<Control-Key-p>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="all",
                                            icon=get_icon(ICO_PULL_ALL),
                                            command=lambda: pull_all_workspace(),
                                        ),
                                        TileLabelButton(
                                            caption="fetch",
                                            commandtext="selected",
                                            icon=get_icon(ICO_FETCH),
                                            command=lambda: on_fetch_tracked(),
                                            hotkey="<Control-Key-P>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="all",
                                            icon=get_icon(ICO_FETCH_ALL),
                                            command=lambda: fetch_all_workspace(),
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
                                        ("branch", None),
                                        ("file", None),
                                        ("unstaged", None),
                                        ("staged", None),
                                        ("type", None),
                                    ],
                                    header_width=(
                                        150, 100, 250, 100, 100, 100),
                                    height=13,
                                    on_double_click=lambda x: on_add_or_undo(
                                        x),
                                    on_right_click=lambda cntrl, ctx: on_changed_context(
                                        cntrl, ctx),
                                ),
                                TileCols(
                                    source=[
                                        TileLabelButton(
                                            caption="changes",
                                            commandtext="refresh",
                                            icon=get_icon(ICO_REFRESH),
                                            command=lambda: set_changes(),
                                            hotkey="<F1>",
                                        ),
                                        TileLabelButton(
                                            caption="all",
                                            commandtext="select",
                                            icon=get_icon(ICO_SEL_ALL),
                                            command=lambda: gt("changes").set_selection(
                                                -1
                                            ),
                                            hotkey="<F2>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="unselect",
                                            icon=get_icon(ICO_CLR_ALL),
                                            command=lambda: gt(
                                                "changes"
                                            ).clr_selection(),
                                            hotkey="<F3>",
                                        ),
                                    ]
                                ),
                                TileCols(
                                    source=[
                                        TileLabelButton(
                                            caption="selected",
                                            commandtext="add",
                                            icon=get_icon(ICO_FILE_ADD),
                                            command=lambda: on_add(),
                                            hotkey="<Alt-Key-a>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="unstage",
                                            icon=get_icon(ICO_FILE_SUB),
                                            command=lambda: on_add_undo(),
                                            hotkey="<Alt-Key-q>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="diff",
                                            icon=get_icon(ICO_FILE_DIFF),
                                            command=lambda: on_diff(),
                                            hotkey="<Alt-Key-w>",
                                        ),
                                        TileLabelButton(
                                            idn="black",
                                            caption="",
                                            commandtext="autoformat source",
                                            icon=get_icon(
                                                ICO_FILE_FORMATSOURCE),
                                            command=lambda: on_formatter(),
                                            hotkey="<Alt-Key-f>",
                                        ),
                                        TileLabelButton(
                                            idn="difftool",
                                            caption="",
                                            commandtext="difftool",
                                            icon=get_icon(ICO_FILE_DIFFTOOL),
                                            command=lambda: on_difftool(),
                                            hotkey="<Alt-Key-d>",
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
                                TileCols(
                                    source=[
                                        TileEntryCombo(
                                            caption="message:",
                                            idn="commit_short",
                                            width=50,
                                            on_select=lambda x, v: on_sel_commit(
                                                x),
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="clear",
                                            icon=get_icon(ICO_CLR),
                                            command=lambda: on_clr_commit(),
                                            hotkey="<Alt-Key-c>",
                                        ),
                                    ]
                                ),
                                TileEntryText(
                                    caption="", idn="commit_long", width=80, height=10
                                ),
                                TileCols(
                                    source=[
                                        TileLabelButton(
                                            caption="tracked git's",
                                            commandtext="commit",
                                            icon=get_icon("file-signature"),
                                            command=lambda: on_commit(),
                                            hotkey="<Alt-Key-x>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="push",
                                            icon=get_icon("upload"),
                                            command=lambda: on_push_tracked(),
                                            hotkey="<Alt-Key-s>",
                                        ),
                                        TileLabelButton(
                                            caption="",
                                            commandtext="commit + push",
                                            icon=get_icon(
                                                "wand-magic-sparkles"),
                                            command=lambda: on_commit_push_tracked(),
                                            hotkey="<Alt-Key-e>",
                                        ),
                                        TileCheckbutton(
                                            caption="push tags",
                                            idn="push_tags",
                                            on_click=lambda x: write_config(),
                                        ),
                                        TileCheckbutton(
                                            caption="clear message after commit",
                                            idn="clear_after_commit",
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
                                            icon=get_icon(ICO_TRASH),
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
                    (
                        "expert",
                        TileRows(
                            source=[
                                TileLabel(caption=""),
                                TileEntryText(
                                    caption="",
                                    idn="expert_log",
                                    height=20,
                                    width=80,
                                    readonly=True,
                                ),
                                TileCols(
                                    source=[
                                        TileLabelButton(
                                            caption="",
                                            commandtext="clear",
                                            icon=get_icon(ICO_TRASH),
                                            command=lambda: on_expert_clr(),
                                        ),
                                        TileCheckbutton(
                                            caption="follow log",
                                            idn="dev_follow",
                                            on_click=lambda x: write_config(),
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        dev_mode,
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
                    #                     TileLabelClick(
                    #                         caption=f"DONATE to gitonic - {url_sponsor}",
                    #                         on_click=lambda x: open_sponsor_page(),
                    #                     ),
                ]
            ),
        ]
    )
    return main


# gui handling


def open_homepage():
    webbrowser.get().open(url_homepage, new=0)


def open_sponsor_page():
    webbrowser.get().open(url_sponsor, new=0)


def on_sel_all_gits():
    dgb_pr("on_sel_all_gits")
    gt("gits").set_selection(-1)
    set_tracked_gits()


def on_unsel_all_gits():
    dgb_pr("on_sel_all_gits")
    gt("gits").clr_selection()
    set_tracked_gits()


def _run_diff_tool(path, file, callb=None):
    # todo rework with gitutil -> git_difftool
    dgb_pr("_run_diff_tool", path, file)

    from .gitutil import GIT

    cwd = os.getcwd()

    try:
        os.chdir(path)
        if os.getcwd() != path:
            raise Exception("path not exist", path)
        args = [GIT, "difftool", file]
        rc = os.spawnvpe(os.P_NOWAIT, args[0], args, os.environ)
    except Exception as ex:
        dgb_pr(ex)

    os.chdir(cwd)

    return ["difftool", file]


def on_cmd_diff(info, diff_, ignore_switch=False):
    dgb_pr(info)
    sel = gt("changes").get_selection_values()
    run_first = True
    for rec in sel:
        if rec["type"] == "file":

            gitnam = rec["git"]
            do_log(f"--- {gitnam}")

            pg = FileStat(gitnam).name
            git = gws.find(pg)[0]

            logs = []
            rc = diff_(git.path, rec["file"], callb=logs.append)

#             if run_first and len(sel) > 1:
#                 run_first = False
#                 # todo rework -> freezing screen
#                 # todo add input field on settings tab
#                 time.sleep(0.5)

            dgb_pr(f"--- {git}")
            [dgb_pr(x) for x in rc]
            do_log_time(info, ignore_switch=ignore_switch)
            do_logs(rc)
            do_logs_opt(logs)


def on_diff():
    on_cmd_diff("on_diff", git_diff)


def on_difftool():
    # todo rework with gitutil -> git_difftool
    on_cmd_diff("on_difftool", _run_diff_tool, True)


def strip_non_ascii(s):
    import string

    rc = ""
    for c in s:
        if c in string.printable:
            rc += c
    return rc


def ext_iter(k):
    if "," not in k:
        dgb_pr("found formatter ex", k)
        yield k
        return

    for ex in k.split(","):
        dgb_pr("found formatter ex", ex)
        yield ex.strip()


def elements_iter(adict, keypath=[]):
    """deep elements iterator"""
    def _iter(x): return x.items()
    if type(adict) == list:
        _iter = enumerate

    for k, v in _iter(adict):
        keypath = [*keypath, k]

        if type(v) in [list, dict]:
            yield from elements_iter(v, keypath)
            continue

        def setr(nv):
            adict[k] = nv

        yield keypath, v, setr


def expand_all_vars(v):

    for keypath, val, setr in elements_iter(v):
        org_val = str(val)
        val = os.path.expanduser(val)
        # val = os.path.expandvars(val)
        setr(val)

        # todo logging
        if org_val != val:
            dgb_pr("expanded", val)

    return v


def read_formatter_settings():
    frmt_cfg = FileStat(fconfigdir.name).join(["formatter.json"])
    if frmt_cfg.exists() is False:
        dgb_pr("no formatter config file")
        return None
    dgb_pr("found formatter config file")
    with open(frmt_cfg.name) as f:
        c = f.read()
        cfg = json.loads(c)
    normdict = {}
    for ki, v in cfg.items():
        for k in ext_iter(ki):
            lower_k = k.lower()
            # todo check for double entries
            normdict[k.lower()] = expand_all_vars(v)
    return normdict


def on_formatter():
    dgb_pr("on_formatter")
    sel = gt("changes").get_selection_values()

    s = []

    def adder(st):
        # todo tkinter cant handle all utf-8 chars
        s.append(strip_non_ascii(st))

    cfg = read_formatter_settings()
    if cfg is None:
        cfg = {".py": {"cmd": "black", "para": ["%file"]}}

    for rec in sel:
        gitnam = rec["git"]
        repo = FileStat(gitnam).name
        fnam = rec["file"]
        p = FileStat(repo).join([fnam])

        fext = p.splitext()[1].lower()
        if fext not in cfg.keys():
            s.append("---skipping file. no formatter found---")
            s.append(p.name)
            continue

        p = p.name

        s.append("---run formatter---")
        s.append(p)
        frmt_cmd = cfg[fext]["cmd"]
        frmt_para = cfg[fext]["para"]

        if type(frmt_para) != list:
            frmt_para = [frmt_para]

        frmt_para = map(lambda x: x.replace("%file", p), frmt_para)

        cmd = [frmt_cmd, *frmt_para]
        s.append(str(cmd))

        rc = run_proc(cmd, callb=adder)

    do_log_time("running formatter", ignore_switch=False)
    do_logs(s)


def on_log_clr():
    gt("log").clr()
    dgb_pr("on_log_clr")


def do_log_max_history():
    dgb_pr("do_log_max_history")
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
    dgb_pr("do_log_time", x)
    do_log_show(ignore_switch)
    log = gt("log")
    ts = time.asctime(time.localtime(time.time()))
    log.append(f"\n\n\n--- {x} --- {ts}")
    on_follow_log()


def do_log(x=""):
    dgb_pr("do_log", x)
    gt("log").append(x)
    on_follow_log()


def do_logs(x):
    dgb_pr("do_logs", x)
    gt("log").extend(x)
    on_follow_log()


def do_logs_opt(x):
    if x and len(x) > 0:
        dgb_pr("do_logs", x)
        gt("log").extend(x)
        on_follow_log()
        do_log_show()


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
            dgb_pr(tracked, "->", tracked_gits)
            sel_tracked()
    except Exception as ex:
        dgb_pr(ex)


def sel_tracked():
    gt("gits").set_selection(tracked_gits)


def on_gits_cmd(info, selcmd_, gits, ignore_switch=False, update_change=False):
    do_log_time(info, ignore_switch)
    for rec in gits:
        gitnam = rec["git"]
        pg = FileStat(gitnam).name
        git = gws.find(pg)[0]
        logs = []
        rc = selcmd_(git.path, [rec["file"]], callb=logs.append)
        dgb_pr(f"--- {git}")
        [dgb_pr(x) for x in rc]
        do_logs(rc)
        do_logs_opt(logs)
    if update_change:
        set_changes()


def call_mult_gits(gits, gitfunc, msgtxt):
    dgb_pr("on_", msgtxt)
    for gnam in gits:
        try:
            git = gws.find(gnam)[0]
            logs = []
            rc = gitfunc(git.path, callb=logs.append)
            dgb_pr(f"--- {git}")
            [dgb_pr(x) for x in rc]
            do_log_time(f"{msgtxt}: {git.path}")
            do_logs(rc)
            do_logs_opt(logs)
        except Exception as ex:
            dgb_pr(ex)
    set_changes()


def fetch_gits(gits):
    call_mult_gits(gits, git_fetch, "fetch")


def pull_gits(gits):
    call_mult_gits(gits, git_pull, "pull")


def on_fetch_tracked():
    fetch_gits(tracked_gits)


def fetch_all_workspace():
    fetch_gits(sorted(gws.gits.keys()))


def on_pull_tracked():
    pull_gits(tracked_gits)


def pull_all_workspace():
    pull_gits(sorted(gws.gits.keys()))


def on_sel_cmd(info, selcmd_, ignore_switch=False, update_change=False):
    dgb_pr(info)
    gits = gt("changes").get_selection_values()
    on_gits_cmd(
        info, selcmd_, gits, ignore_switch=ignore_switch, update_change=update_change
    )


def on_add():
    on_sel_cmd("on_add", git_add, True, True)


def on_add_undo():
    on_sel_cmd("on_add_undo", git_add_undo, True, True)


def on_add_or_undo(cntrl):
    vals = cntrl.get_selection_values()
    file = vals[0]
    if file["unstaged"] != "":
        on_add()
    else:
        on_add_undo()


def on_changed_context(cntrl, ctx):
    # dgb_pr
    print("on_changed_context", ctx)
    global changes
    row_no = ctx.row[1]
    col_no = ctx.column[1]

    print(changes)
    gnam_base = changes[row_no]['git']
    fnam_base = changes[row_no]['file']

    gnam = FileStat(gnam_base)
    gnam_dir = gnam.name

    fnam = FileStat(gnam_base).join([fnam_base])
    fnam_dir = fnam.dirname()
    fnam_dirnam = fnam.dirname()[len(gnam.name) + 1:]

    dgb_pr(gnam_base, gnam)
    dgb_pr(fnam_base, fnam)

    git = gws.find(gnam)

    ctxmenu = ContextMenu(cntrl._treeview, ctx)

    def open_explorer(fnam):
        def _call(x):
            open_file_explorer(fnam)
        return _call

    ctxmenu.add_command(
        f"open project folder {gnam_base}", open_explorer(gnam_dir))
    if gnam_base != fnam_dirnam:
        ctxmenu.add_command(
            f"open file folder {fnam_dirnam}", open_explorer(fnam_dir))

    load_and_set_context_settings(ctxmenu, gnam_dir, fnam_dir, fnam.name)
    ctxmenu.show()


def replace_all_vars(d, env):

    for keypath, val, setr in elements_iter(d):
        org_val = str(val)
        for k, v in env.items():
            if type(val) == str:
                val = val.replace(k, v)
                val = os.path.expanduser(val)
                setr(val)

    return d


def load_and_set_context_settings(ctxmenu, gnam_dir, fnam_dir, fnam):
    ctx_cfg = FileStat(fconfigdir.name).join(["context.json"])
    if ctx_cfg.exists() is False:
        dgb_pr("no context config file")
        return None

    try:
        with open(ctx_cfg.name) as f:
            c = f.read()
            cfg = json.loads(c)
    except:
        dgb_pr("json parsing error")
        return

    file_short = FileStat(fnam).basename()

    env = {"$GIT": gnam_dir, "$PATH": fnam_dir, "$NAME" : file_short,
           "$FILE": fnam, "$PYTHON": sys.executable}
    dgb_pr("env: " + str(env))

    cfg = replace_all_vars(cfg, env)
    dgb_pr(cfg)

    for _, ctxset in cfg.items():

        workdir = ctxset.setdefault("workdir", ".")
        dgb_pr("workdir for command", workdir)

        patnli = ctxset["expr"]
        if patnli:
            patnli = patnli if type(patnli) == list else [patnli]
            found = False
            for patn in patnli:
                found = fnmatch.fnmatch(fnam, patn)
                if found:
                    break
            if found is False:
                continue

        ctxmenu.add_separator()
        for mi in ctxset["menu"]:
            def _run(args):
                def _runner(x):
                    if args is None or len(args) == 0:
                        return
                    dgb_pr("run command", *args)

                    with PushDir(workdir) as pd:
                        rc = os.spawnvpe(
                            os.P_NOWAIT, args[0], args, os.environ)
                        dgb_pr("call result", rc)

                return _runner
            ctxmenu.add_command(
                mi[0], _run(mi[1]))


fcommit = FileStat(fconfigdir.name).join(["commit.json"])
commit_history = []


def read_commit():
    global commit_history
    try:
        with open(fcommit.name) as f:
            cont = f.read()
            commit_history = json.loads(cont)
    except Exception as ex:
        dgb_pr(ex)
    set_commits()


def write_commit():
    try:
        with open(fcommit.name, "w") as f:
            cont = json.dumps(commit_history, indent=4)
            f.write(cont)
    except Exception as ex:
        dgb_pr(ex)


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
    dgb_pr("*********vals", vals)
    commits.set_values(vals)
    if len(vals) > 0:
        commits.set_index(0)
        gt("commit_long").set_val(commit_history[0]["long"])

    apply_clear_after_commit()


def on_sel_commit(idx):
    dgb_pr(idx)
    # gt("commit_short").set_val(commit_history[idx]["short"])
    gt("commit_long").set_val(commit_history[idx]["long"])


def on_clr_commit():
    # todo bring tab top front
    gt("maintabs").select("tab_commit")
    gt("commit_short").clr().focus()
    gt("commit_long").clr()


def on_commit():
    dgb_pr("on_commit")
    head = gt("commit_short").get_val().strip()
    body = gt("commit_long").get_val().strip()

    if len(head) < min_commit_length or len(head) > 50:

        gt("maintabs").select("tab_commit")

        tkinter.messagebox.showerror(
            "error",
            f"length: {min_commit_length} >= message < 50\ncurrent: {len(head)}",
        )

        gt("commit_short").focus()

        return False

    apply_clear_after_commit()

    message = head
    if len(body) > 0:
        message += "\n" * 2 + body

    add_commit_history(head, body)

    for gnam in tracked_gits:
        try:
            dgb_pr("use", gnam)
            git = gws.find(gnam)[0]
            do_log_time(f"commit: {git.path} '{message}'")
            if git.has_staged():
                logs = []
                rc = git_commit(git.path, message, callb=logs.append)
                dgb_pr(f"--- {git}")
                [dgb_pr(x) for x in rc]
                do_logs(rc)
                do_logs_opt(logs)
                do_log("commited staged files")
            else:
                do_log("nothing staged")

        except Exception as ex:
            dgb_pr(ex)

    set_changes()

    return True


def on_cmd_push(info, push_, gits):
    dgb_pr(info)
    sel = gt("changes").get_selection_values()
    do_log_time(info)
    for pg in gits:
        git = gws.find(pg)[0]
        logs = []
        rc = push_(git.path, callb=logs.append)
        [dgb_pr(x) for x in rc]
        do_log()
        do_log(f"--- push: {git}")
        do_logs(rc)
        do_logs_opt(logs)
        if push_tags:
            logs = []
            rc = git_push_tags(git.path, callb=logs.append)
            [dgb_pr(x) for x in rc]
            do_log()
            do_log(f"--- push tags: {git}")
            do_logs(rc)
            do_logs_opt(logs)


def on_push_tracked():
    dgb_pr("on_push_tracked")
    cmd_ = git_push
    on_cmd_push(
        "on_push_tracked",
        cmd_,
        tracked_gits,
    )


def on_commit_push_tracked():
    if on_commit():
        on_push_tracked()


def on_push_all_workspace():
    dgb_pr("on_push_all_workspace")
    cmd_ = git_push
    on_cmd_push(
        "on_push_all_workspace",
        cmd_,
        sorted(gws.gits.keys()),
    )


# init


def set_workspace(update=True):
    dgb_pr("refresh_workspace")
    global gws
    gws = GitWorkspace(frepo)
    gws.refresh()
    gt("gits").set_values(sorted(gws.gits.keys()))
    dgb_pr("gws", gws)
    # gws.refresh_status()
    if update:
        tracked_read()
        set_tracked_gits()


def set_tracked_gits(update=True):
    dgb_pr("set_tracked_gits")
    global tracked_gits
    tracked_gits = gt("gits").get_selection_values()
    tracked_gits = list(map(lambda x: x[1], tracked_gits))
    dgb_pr("tracked_gits", tracked_gits)
    tracked_write()
    if update:
        set_changes()


def set_changes():
    dgb_pr("set_changes")
    global changes
    changes = []

    gits = list(map(lambda x: (x, gws.find(x)), tracked_gits))
    dgb_pr(gits)

    for path_git in gits:
        path, git = path_git

        dgb_pr(path, git)

        fs = FileStat(path, prefetch=True)
        if not fs.exists():
            continue

        userhome = os.path.expanduser("~")

        gitnam = fs.name  # fs.basename()
        if gitnam.startswith(userhome + os.sep):
            gitnam = gitnam.replace(userhome, "~")

        git = git[0]
        git.refresh_status()

        if len(git.status) > 0:
            for stat in git.status:
                fs = git.stat(stat)
                fs_ex = fs.exists()

                bnam = git.current_branch.bnam if git.current_branch else ""

                gst = {
                    "git": gitnam,
                    "branch": bnam,
                    "file": stat.file,
                    "unstaged": stat.mode,
                    "staged": stat.staged,
                    "type": ("file" if fs.is_file() else "dir")
                    if fs_ex
                    else "---deleted---",
                }
                changes.append(gst)
    gt("changes").set_values(changes)


def apply_clear_after_commit():
    if clear_after_commit:
        gt("commit_short").set_val("")
        gt("commit_long").set_val("")


def startup_gui():
    # read_config()
    read_commit()
    set_workspace(True)

    #     gt("difftool").set_enabled(False)
    #     gt("black").set_enabled(False)

    gt("follow").set_val(follow)
    gt("auto_switch").set_val(auto_switch)
    gt("push_tags").set_val(push_tags)
    gt("show_changes").set_val(show_changes)
    gt("clear_after_commit").set_val(clear_after_commit)
    gt("dev_mode").set_val(dev_mode)
    if dev_mode:
        gt("dev_follow").set_val(dev_follow)
        gt("dev_follow_max").set_val(dev_follow_max)

    if show_changes or len(changes) > 0:
        gt("maintabs").select("tab_changes")
