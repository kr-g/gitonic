#!/usr/bin/env python3

import sys
import os
import fnmatch
import queue

#

from core.logs import LogOutHandler
from gtcommon import EXPERT_LOG, REPO_LOG, logex, logrepo

from giton import RepoLog

#

from core.file import FileStat, PushDir
from core.sysutil import get_terminal_size, open_file_explorer

#

from tkui.tkuicore import tk_show_error
from tkui.singleinstance import switch2instance, tk_bg_bring_to_front, cleanup_single_instance

from tkui.tkuiapp import ui_app, root, tk_add_bg_callb, tk_get_root
from tkui.tkuiwidg import TNContextMenu

from core.gitonapp import (GitonicApp, FetchCmd, PullCmd, CommitCmd,
                           RefreshCmd, PushCmd, PushTagsCmd,
                           GetTagsCmd, StageFileCmd, UnstageFileCmd,
                           CommitMessageCmd, DiffFileCmd, DiffToolFileCmd)

from core.gitcmd import set_git_exe, get_git_exe

from core.task import CmdTask
from core.runr import PoolTaskRunner, RepoTaskRunner

#

from core.const import CFG_WORKSPACE  # , CFG_WORKSPACE_DEFAULT
from core.const import CFG_CLEAR_COMMIT, CFG_CLEAR_COMMIT_DEFAULT
from core.const import CFG_PUSH_TAGS, CFG_PUSH_TAGS_DEFAULT
from core.const import CFG_MAX_RECORDS, CFG_MAX_RECORDS_DEFAULT
from core.const import CFG_DEV_FOLLOW_MAX, CFG_DEV_FOLLOW_MAX_DEFAULT
from core.const import CFG_DEV_FOLLOW, CFG_DEV_FOLLOW_DEFAULT
from core.const import CFG_DEV_MODE, CFG_DEV_MODE_DEFAULT
from core.const import CFG_LOG_FOLLOW, CFG_LOG_FOLLOW_DEFAULT
from core.const import CFG_SHOW_CHANGES_TAB, CFG_SHOW_CHANGES_TAB_DEFAULT
from core.const import CFG_MAX_COMMIT, CFG_MAX_COMMIT_DEFAULT
from core.const import CFG_MIN_COMMIT_LENGTH, CFG_MIN_COMMIT_LENGTH_DEFAULT
from core.const import P_THREADS, P_THREADS_DEFAULT
from core.const import VERSION, PATH, CFG_GIT


#

_debug = not False


#

MAX_LOG_ITEMS = 15*3
LOG_TASK_TOUT = 15


class LogViewFilterer(object):

    filters = {}

    def __init__(self, reponame):
        self.reponame = reponame

        self._run = True
        self.log = RepoLog.getLogHandler(self.reponame).strip()

        assert self.reponame
        self.widg = ui_app.pane_log.get_other_log(self.reponame)

        LogViewFilterer.filters[self.reponame] = self

    @staticmethod
    def reponames():
        return LogViewFilterer.filters.keys()

    @staticmethod
    def remove_name(reponame):
        if reponame in LogViewFilterer.filters:
            LogViewFilterer.filters[reponame].remove()

    def remove(self):
        self.stop()
        del LogViewFilterer.filters[self.reponame]
        ui_app.pane_log.rm_other_log(self.reponame)
        logex.info("logfilter cleanup", self.reponame)

    def stop(self):
        logex.info("logfilter stop", self.reponame)
        self._run = False

    def run_dump_task(self):
        from queue import Empty

        if self._run is False:
            return

        added = 0

        try:
            for i in range(1, MAX_LOG_ITEMS):

                msg = self.log.get_nowait()

                self.widg.append(msg)

                logex.info("logfilter", self.reponame, msg)

                added += 1

        except Empty:
            pass

        if added > 0:
            _log_post(self.widg)

        tk_add_bg_callb(self.run_dump_task, force=True,
                        force_tout=LOG_TASK_TOUT)


#


def refresh_tracked_from_workspace():
    logex.info("refresh_tracked_from_workspace")
    app.refresh_tracked()
    # ui_app.pane_tracked.tracked = app.tracked_short

    # todo
    app.wsprop = ui_app.pane_tracked.workspaces

    refresh_repos_only()
    switch_changes()


def refresh_repos_only():
    all_repos = list(app.workspace_all_repo_iter())
    all_repos = list(map(lambda x: FileStat.collapseuser(x), all_repos))
    logex.info("all_repos")
    logex.info(all_repos)
    logex.info("repos short")
    logex.info(app.tracked_short)

    ui_app.pane_tracked.tracked = all_repos
    ui_app.pane_tracked.tracked.select_values(app.tracked_short)

    update_deps()


def update_deps():

    sel_vals = ui_app.pane_tracked.tracked.selected_values()
    logex.info("sel_vals")
    logex.info(sel_vals)

    app.save_tracked(sel_vals)

    ui_app.pane_changes.clr_items()

    # remove existing log filter queue

    filternames = list(LogViewFilterer.reponames())
    for lnam in filternames:
        logex.info("check log queue", lnam)
        if lnam not in app.tracked_short:
            LogViewFilterer.remove_name(lnam)
            logex.info("remove log queue", lnam)

    # add log filter and views, setup dump task

    filternames = list(LogViewFilterer.reponames())
    for lnam in app.tracked_short:
        if lnam not in filternames:
            LogViewFilterer(lnam).run_dump_task()
            logex.info("add log queue", lnam)

    #

    ui_app.set_mouse_pointer(busy=True)

    all_repos = ["--- all ---", *app.tracked_short]

    # set focus elements
    ui_app.pane_changes.repos.set_values(all_repos)
    # todo keep state if unchanged
    ui_app.pane_changes.repos.clr_selection()
    ui_app.pane_changes.repos.select_index(0)

    # set focus elements
    ui_app.pane_log.repos.set_values(all_repos)
    # todo keep state if unchanged
    ui_app.pane_log.repos.clr_selection()
    ui_app.pane_log.repos.select_index(0)
    ui_app.pane_log.show_all_log()

    # prepare thread and sorting
    cmd = RefreshCmd(app).setup().add(
        lambda: app.sort_refs() and False)  # .complete()

    def _bg_refresh_task():
        if cmd.loop():
            tk_add_bg_callb(_bg_refresh_task)
        else:
            ui_app.set_mouse_pointer()

            logex.info(app.refs)

            filter_files()

            # show changes tab
            # todo

    # call thread and other tasks in tk event loop
    _bg_refresh_task()


def switch_changes():
    if len(app.refs) > 0 or app.base.getbool(CFG_SHOW_CHANGES_TAB, CFG_SHOW_CHANGES_TAB_DEFAULT):
        ui_app.select_tab()


def filter_files(repo=None):

    ui_app.pane_changes.clr_items()

    ui_app.filtered = []

    for ref in app.refs:

        if repo is not None:
            # todo
            if FileStat(ref.repo.path).name != FileStat(repo).name:
                continue

        bnam = ref.repo.current_branch.bnam if ref.repo.current_branch else ""

        fs = FileStat(ref.repo.path).join([ref.file.file])
        fs_ex = fs.exists()

        _typ = ("file" if fs.is_file() else "dir") if fs_ex else "---deleted---"

        ui_app.filtered.append(ref)
        ui_app.pane_changes.add_item(ref.idx,
                                     bnam,
                                     ref.file.file,
                                     ref.file.staged,
                                     ref.file.mode,
                                     _typ)

    sel_filtered_changes()


def add_to_tracked(curval):
    logex.info("add_to_tracked")

    update_deps()


def add_all_to_tracked():
    logex.info("add_all_to_tracked")
    ui_app.pane_tracked.tracked.select_values(-1)

    update_deps()


def remove_all_from_tracked():
    logex.info("remove_all_from_tracked")
    ui_app.pane_tracked.tracked.select_values(None)

    update_deps()

#


def run_cmd_as_bg_task(cmd, callb=None):

    def _bg_refresh_task():
        if cmd.loop():
            tk_add_bg_callb(_bg_refresh_task)
        else:
            ui_app.set_mouse_pointer()

            if callb:
                tk_add_bg_callb(callb)

    ui_app.set_mouse_pointer(busy=True)
    _bg_refresh_task()

#


def fetch_all_tracked():
    logex.info("fetch_all_tracked")

    cmd = FetchCmd(app).setup()
    run_cmd_as_bg_task(cmd)


def pull_all_tracked():
    logex.info("pull_all_tracked")

    cmd = PullCmd(app).setup()
    run_cmd_as_bg_task(cmd)

#


def on_change_repo_click(selected):
    logex.info("on_change_repo_click", selected)
    repo = None
    if selected[0] - 1 >= 0:
        repo = app.tracked_short[selected[0]-1]
    logex.info("filter", repo)
    filter_files(repo)


def on_change_repo_clickr(ctx):
    logex.info("on_change_repo_clickr", ctx)

    row = ctx.row

    if row == 0:
        return

    rowref = app.tracked_short[row-1]

    logex.info("context", row, rowref)

    context_menu = TNContextMenu(ui_app.pane_tracked)

    git = rowref

    path = rowref

    logex.info("context", git, path)

    load_and_set_context_settings("changes-all", context_menu, git, path, "")
    load_and_set_context_settings("changes-repo", context_menu, git, path, "")

    context_menu.show(ctx.ev)


def on_change_file_click(selected, sel_nums):
    logex.info("on_change_click", selected, "numbers",
               ", ".join(map(lambda x: str(x), sel_nums)))

    # for n in sel_nums:
    #     logex.info(ui_app.filtered[n])


def on_change_file_click_dbl(ctx):
    logex.info("on_change_click_dbl", ctx)

    row = ctx.row[1]
    logex.info(ui_app.filtered[row])

    logex.info("add/undo", app.refs[row].file)

    if app.refs[row].file.staged in ["", "?"]:
        logex.info("add")
        changes_add_sel()
    else:
        logex.info("add undo")
        changes_undo_sel()


def on_changes_file_clickr(ctx):
    logex.info("on_changes_file_click_r", ctx)

    row = ctx.row[1]
    rowref = app.refs[row]

    logex.info("context", row, rowref)

    context_menu = TNContextMenu(ui_app.pane_changes.treechanges)

    git = FileStat(rowref.repo.path).collapse()
    file = rowref.file.file

    path = FileStat(git).join([file]).dirname()
    path = FileStat.collapseuser(path)

    logex.info("context", git, path, file)

    load_and_set_context_settings("changes-all", context_menu, git, path, file)
    load_and_set_context_settings(
        "changes-file", context_menu, git, path, file)

    context_menu.show(ctx.ev)


def changes_refresh():
    logex.info("changes_refresh")
    refresh_repos_only()


def changes_sel_all():
    # todo remove
    logex.info("changes_sel_all")
    for idx, x in enumerate(ui_app.filtered):
        ui_app.pane_changes.treechanges.select_row(idx)


def changes_unsel_all():
    logex.info("changes_unsel_all")
    ui_app.pane_changes.treechanges.clr_selection()


def select_changes(mode=True):
    logex.info("filtered", ui_app.filtered)
    selrows = ui_app.pane_changes.treechanges.get_selected_rows()
    logex.info(f"selected mode {mode}", selrows,)

    all_idx = [str(ui_app.filtered[x].idx) for x in selrows]
    logex.info(f"all_idx mode {mode}", all_idx)
    cmd = " ".join(all_idx)

    app.sel_refs(mode, cmd)
    logex.info(f"selected mode {mode}", ", ".join(
        map(lambda x: str(x), [x for x in app.refs if x.sel])))

    sel_filtered_changes()


def sel_filtered_changes():
    ui_app.pane_changes.treechanges.clr_selection()
    for idx, x in enumerate(ui_app.filtered):
        if x.sel:
            ui_app.pane_changes.treechanges.select_row(idx)


def changes_add_sel():
    logex.info("changes_add_sel")
    select_changes()

    cmd = StageFileCmd(app).setup()
    run_cmd_as_bg_task(cmd, changes_refresh)


def changes_undo_sel():
    logex.info("changes_undo_sel")
    select_changes()

    cmd = UnstageFileCmd(app).setup()
    run_cmd_as_bg_task(cmd, changes_refresh)


def changes_diff_sel():
    logex.info("changes_diff_sel")

    sel = ui_app.pane_changes.treechanges.get_selected_rows()
    logex.info("files sel", sel)

    cmd = DiffFileCmd(app).set_sel_files(sel).setup()  # .complete()
    run_cmd_as_bg_task(cmd, lambda: ui_app.select_tab("log"))


#


def changes_format_sel():
    logex.info("changes_format_sel")

    on_formatter()

#


def changes_difftool_sel():
    logex.info("changes_difftool_sel")

    sel = ui_app.pane_changes.treechanges.get_selected_rows()
    logex.info("files sel", sel)

    cmd = DiffToolFileCmd(app).set_sel_files(sel).setup()  # .complete()
    # run_cmd_as_bg_task(cmd)

    ui_app.set_mouse_pointer(busy=True)

    def _bg_task():
        if cmd.loop():
            tk_add_bg_callb(_bg_task)
        else:
            tk_add_bg_callb(lambda: ui_app.set_mouse_pointer(
                busy=False), force=True, force_tout=1000)

    # call thread and other tasks in tk event loop
    _bg_task()

#


def commit_commit(nexttask=None):
    logex.info("commit_commit")

    short = ui_app.pane_commit.msg_cb.get_val()
    long = ui_app.pane_commit.msg_text.get_val()

    minlength = app.base.getint(
        CFG_MIN_COMMIT_LENGTH, CFG_MIN_COMMIT_LENGTH_DEFAULT)

    logex.info("commit len", len(short), "min length", minlength)

    if len(short) < minlength:
        logex.info("message too short", minlength)

        tk_show_error("error", "message text too short")

        return

    CommitMessageCmd(app).setup().push(short, long)

    cmd = CommitCmd(app).setup()

    ui_app.set_mouse_pointer(busy=True)

    def _bg_task():
        if cmd.loop():
            tk_add_bg_callb(_bg_task)
        else:

            if app.base.getbool(CFG_CLEAR_COMMIT, CFG_CLEAR_COMMIT_DEFAULT):
                tk_add_bg_callb(commit_clear)

            tk_add_bg_callb(lambda: ui_app.set_mouse_pointer(
                busy=False), force=True, force_tout=500)

            tk_add_bg_callb(changes_refresh)
            if nexttask:
                tk_add_bg_callb(nexttask)

    # call thread and other tasks in tk event loop
    _bg_task()

#


def commit_push():
    logex.info("commit_push")

    pushtags = ui_app.pane_commit.pushtags_ck.get_val()
    logex.info("push_tags", pushtags)

    cmd = PushCmd(app).setup()

    ui_app.set_mouse_pointer(busy=True)

    def _bg_task_push(cmd):
        if cmd.loop():
            tk_add_bg_callb(lambda: _bg_task_push(cmd))
        else:
            cmd = PushTagsCmd(app).setup() if pushtags else None
            tk_add_bg_callb(lambda: _bg_task_push_tags(cmd))

    def _bg_task_push_tags(cmd):
        if pushtags is True and cmd is not None and cmd.loop():
            tk_add_bg_callb(lambda: _bg_task_push_tags(cmd))
        else:
            tk_add_bg_callb(lambda: ui_app.set_mouse_pointer(
                busy=False), force=True, force_tout=500)

    # call thread and other tasks in tk event loop
    _bg_task_push(cmd)


def commit_magic():
    logex.info("commit_magic")
    commit_commit(commit_push)
    # commit_push()


def commit_combo_changed(curval):
    logex.info("commit_combo_changed")
    try:
        pos = list(ui_app.pane_commit.msg_cb.get_values()).index(curval)
    except:
        pos = -1
    if pos >= 0:
        msglong = app.messages.conf[pos]["long"]
        ui_app.pane_commit.msg_text.set_val(msglong)
        logex.info("long", msglong)
    else:
        msglong = ""
    CommitMessageCmd(app).push(curval, msglong)
    ui_app.pane_commit.msg_cb.set_values(CommitMessageCmd(app).as_shortlist())
    max_size = app.base.getint(CFG_MAX_COMMIT, CFG_MAX_COMMIT_DEFAULT)
    logex.info("max_size", max_size)
    CommitMessageCmd(app).cut_to(max_size)
    # todo save


def commit_clear():
    logex.info("commit_clear")
    ui_app.pane_commit.msg_cb.set_val("")
    ui_app.pane_commit.msg_text.set_val("")


#
main_log = RepoLog.getLogHandler()

#


def log_dump_task():
    try:
        for i in range(1, MAX_LOG_ITEMS):
            s = main_log.get_nowait()
            log_adds(s)
    except:
        pass
    tk_add_bg_callb(log_dump_task, force=True, force_tout=LOG_TASK_TOUT)


#

log_dump_task()

#


def log_adds(s):

    logwidg = ui_app.pane_log.log_detail

    logex.info("log_adds")
    logwidg.append(s)
    _log_post(logwidg)


def log_clr():
    logex.info("log_clr")

    logwidg = ui_app.pane_log.cur_log

    # if on all-tab clr other tabs too
    if logwidg == ui_app.pane_log.log_detail:
        ui_app.pane_log.clr_other_logs()
        logex.info("log_clr", "all others")

    logwidg.clr()
    _log_post(logwidg)

#


def on_filter_log_repo(selected):
    logex.info("on_filter_log_repo", selected)
    repo = None
    if selected[0] > 0:
        repo = app.tracked_short[selected[0]-1]
    filter_log(repo)


def filter_log(repo=None):
    logex.info("log_filter", repo)

    if repo is None:
        ui_app.pane_log.show_all_log()
        return

    thelog = ui_app.pane_log.get_other_log(repo)
    ui_app.pane_log.set_log_visible(thelog)

#

# todo rework
# https://docs.python.org/3/library/logging.handlers.html#logging.handlers.QueueHandler
# https://docs.python.org/3/library/logging.handlers.html#queuelistener


logex_queue = queue.Queue()


def logex_add(x):
    logex_queue.put(x)


def logex_dump_task():
    from queue import Empty
    try:
        for i in range(1, MAX_LOG_ITEMS):
            msg = logex_queue.get_nowait()
            xlog_adds(msg)
    except Empty:
        pass

    tk_add_bg_callb(logex_dump_task, force=True, force_tout=LOG_TASK_TOUT)

#


logex_dump_task()

#


def xlog_adds(s):

    if app.base.getbool(CFG_DEV_MODE, CFG_DEV_MODE_DEFAULT) is False:
        return

    logwidg = ui_app.pane_extralog.logdetail

    logwidg.append(s)
    _log_post(logwidg)


def expertlog_clr():
    logex.info("expertlog_clr")

    logwidg = ui_app.pane_extralog.logdetail

    logwidg.clr()
    _log_post(logwidg)


#


def _log_post(widg):
    cnt = widg.get_line_count()
    maxcnt = app.base.getint(CFG_DEV_FOLLOW_MAX, CFG_DEV_FOLLOW_MAX_DEFAULT)

    # _debug and print("cnt,maxcnt", cnt, maxcnt)

    if cnt > maxcnt:
        last = f"{cnt-maxcnt}.0"
        widg.remove_lines(last=last)

    flw = app.base.getbool(CFG_DEV_FOLLOW, CFG_DEV_FOLLOW_DEFAULT)
    if flw:
        widg.gotoline()


#


def prefs_changed(key, callb=None):
    def _settr(curval):
        app.base.set_val(key, curval)
        logex.info(f"key-changed {key} {curval}")
        logex.info(app.base)

        logex.info("save base config")
        app.base.save()

        if callb:
            callb(key, curval)

    return _settr


#
# formatter
#


def ext_iter(k):
    if "," not in k:
        logex.info("found formatter ex", k)
        yield k
        return

    for ex in k.split(","):
        logex.info("found formatter ex", ex)
        yield ex.strip()


# def strip_non_ascii(s):
#     import string

#     rc = ""
#     for c in s:
#         if c in string.printable:
#             rc += c
#     return rc


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

        if org_val != val:
            logex.info("expanded vars", val)

    return v

#


def read_formatter_settings():
    app.refresh_formatter()
    normdict = {}
    for ki, v in app.formatter.conf.items():
        for k in ext_iter(ki):
            lower_k = k.lower()
            # todo check for double entries
            normdict[lower_k] = expand_all_vars(v)
    return normdict


def on_formatter():
    logex.info("on_formatter")

    cfg = read_formatter_settings()
    if cfg is None:
        cfg = {".py": {"cmd": "autopep8", "para": ["-i", "%file"]}}

    logex.info("formatter", cfg)

    sel = ui_app.pane_changes.treechanges.get_selected_rows()
    logex.info("files sel", sel)

    refs = [app.refs[x] for x in sel]
    logex.info("files to format", refs)

    def formatter_it():
        for r in refs:
            reponame = FileStat(r.repo.path).collapse()
            logex.info("repo", reponame)
            f = FileStat(reponame).join([r.file.file])
            fnam = f.name
            # logex.info("repo",r.repo.path, "file", r.file.file)
            logex.info("file", fnam)

            fext = f.splitext()[1].lower()
            if fext not in cfg.keys():
                logex.info("---skipping file. no formatter found---", fnam)
                continue

            frmt_cmd = cfg[fext]["cmd"]
            frmt_para = cfg[fext]["para"]

            if type(frmt_para) != list:
                frmt_para = [frmt_para]

            # todo
            frmt_para = map(lambda x: x.replace("%file", fnam), frmt_para)
            frmt_para = map(lambda x: x.replace("$file", fnam), frmt_para)
            frmt_para = map(lambda x: x.replace("%FILE", fnam), frmt_para)
            frmt_para = map(lambda x: x.replace("$FILE", fnam), frmt_para)

            cmd = [frmt_cmd, *frmt_para]
            cmds = " ".join(cmd)

            logex.info("formatter cmd", str(cmd))
            logrepo.info(reponame, "formatter", str(cmd))

            def _add():
                r = reponame

                def _inner(s):
                    logrepo.info(r, s)
                return _inner

            def _done():
                r = reponame

                def _inner():
                    logrepo.info(r, "---done---", cmds)
                return _inner

            rcmd = CmdTask().configure(callb=_add(), stop_callb=None,
                                       done_callb=_done()).set_command(cmds)

            yield rcmd

    def _make_runner():
        maxthreads = app.base.getint(P_THREADS, P_THREADS_DEFAULT)
        logex.info("maxthreads", maxthreads)

        all_tasks = formatter_it()

        def _y(x):
            yield x

        all_tasks_it = map(_y, all_tasks)

        # todo rework RepoTaskRunner interface wrt. PoolTaskRunner
        rcmd = [RepoTaskRunner("---", x) for x in all_tasks_it]
        logex.info("runner total", len(rcmd))

        pool = PoolTaskRunner(rcmd, maxthreads=maxthreads)

        def poolrun():

            rc = pool.loop()
            return rc

        return poolrun

    def _bg_run():
        if runner():
            tk_add_bg_callb(_bg_run, force=True, force_tout=LOG_TASK_TOUT)
        else:
            ui_app.set_mouse_pointer(busy=False)

    ui_app.set_mouse_pointer(busy=True)
    runner = _make_runner()
    _bg_run()

#
# context handler
#


def replace_all_vars(d, env):

    for keypath, val, setr in elements_iter(d):
        org_val = str(val)
        for k, v in env.items():
            if type(val) == str:
                val = val.replace(k, v)
                val = os.path.expanduser(val)
                setr(val)

    return d


def load_and_set_context_settings(sect, ctxmenu, gnam_dir, fnam_dir, fnam):

    logex.info("ctx para", gnam_dir, fnam_dir, fnam)

    app.refresh_context()
    cfg = app.contextopts.conf

    gnam_dir = FileStat(gnam_dir).collapse()
    fnam_dir = FileStat(gnam_dir).join([fnam]).collapse()

    path = FileStat(fnam_dir).dirname()
    path_dir = FileStat(path).collapse()

    file_short = FileStat(fnam_dir).basename()

    env = {"$_GIT": gnam_dir, "$GIT": FileStat(gnam_dir).name, "$_PATH": path_dir,
           "$PATH": FileStat(path_dir).name, "$NAME": file_short, "$_FILE": fnam_dir,
           "$FILE": FileStat(fnam_dir).name, "$PYTHON": sys.executable}

    logex.info("env: " + str(env))

    cfg = replace_all_vars(cfg, env)
    logex.info("context", cfg)

    for _, ctxset in cfg.items():

        workdir = ctxset.setdefault("workdir", ".")
        logex.info("workdir for command", workdir)

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

        if sect in ctxset:
            ctxmenu.add_separator()
            for mi in ctxset[sect]:
                def _run(args):
                    def _runner(x):
                        if args is None or len(args) == 0:
                            return
                        logex.info("run command", *args)

                        with PushDir(workdir):
                            rc = os.spawnvpe(
                                os.P_NOWAIT, args[0], args, os.environ)
                            logex.info("call result", rc)

                    return _runner

                nam = mi["name"]

                ctxmenu.add_command(
                    nam, _run(mi["para"]))

#
#
#
app = None

def run_main():
    global app
    
    if switch2instance(PATH):
        logex.info("allready running. switch to instance")
        sys.exit()

    tk_get_root().add_quit_handler(cleanup_single_instance)

    app = GitonicApp()

    # cmd = RefreshCmd(app).setup().complete()
    # app.sort_refs()

    # tracked

    ui_app.pane_tracked._workspaces.on_change = prefs_changed(CFG_WORKSPACE)

    ui_app.pane_tracked.workspaces = app.wsprop

    ui_app.pane_tracked.tracked.on_click = add_to_tracked
    ui_app.pane_tracked.refresh_btn.on_click = refresh_tracked_from_workspace
    ui_app.pane_tracked.selall_btn.on_click = add_all_to_tracked
    ui_app.pane_tracked.unselall_btn.on_click = remove_all_from_tracked
    ui_app.pane_tracked.fetch_btn.on_click = fetch_all_tracked
    ui_app.pane_tracked.pull_btn.on_click = pull_all_tracked

    # todo remove
    # ui_app.pane_tracked.tracked = app.tracked_short

    # changes

    ui_app.pane_changes.repos.on_click = on_change_repo_click
    ui_app.pane_changes.repos.on_clickr = on_change_repo_clickr
    ui_app.pane_changes.treechanges.on_click = None  # on_change_file_click
    ui_app.pane_changes.treechanges.on_clickr = on_changes_file_clickr
    ui_app.pane_changes.treechanges.on_click_dbl = on_change_file_click_dbl

    ui_app.pane_changes.refreshchanges_btn.on_click = changes_refresh
    ui_app.pane_changes.selallchanges_btn.on_click = changes_sel_all
    ui_app.pane_changes.unselallchanges_btn.on_click = changes_unsel_all
    ui_app.pane_changes.addchanges_btn.on_click = changes_add_sel
    ui_app.pane_changes.undochanges_btn.on_click = changes_undo_sel
    ui_app.pane_changes.diffchanges_btn.on_click = changes_diff_sel
    ui_app.pane_changes.autoformchanges_btn.on_click = changes_format_sel
    ui_app.pane_changes.difftoolchanges_btn.on_click = changes_difftool_sel

    # commit

    ui_app.pane_commit.msg_cb.on_change = commit_combo_changed
    ui_app.pane_commit.msg_clr_btn.on_click = commit_clear
    ui_app.pane_commit.pushtags_ck.on_change = prefs_changed(CFG_PUSH_TAGS)
    ui_app.pane_commit.clrcommit_ck.on_change = prefs_changed(CFG_CLEAR_COMMIT)

    ui_app.pane_commit.commit_btn.on_click = commit_commit
    ui_app.pane_commit.push_btn.on_click = commit_push
    ui_app.pane_commit.magic_btn.on_click = commit_magic

    ui_app.pane_commit.pushtags_ck.set_val(
        app.base.getbool(CFG_PUSH_TAGS, CFG_PUSH_TAGS_DEFAULT))
    ui_app.pane_commit.clrcommit_ck.set_val(
        app.base.getbool(CFG_CLEAR_COMMIT, CFG_CLEAR_COMMIT_DEFAULT))

    lmsgshort = CommitMessageCmd(app).as_shortlist()
    ui_app.pane_commit.msg_cb.set_values(lmsgshort)

    msgshort, msglong = CommitMessageCmd(app).top()
    ui_app.pane_commit.msg_cb.set_val(msgshort)
    ui_app.pane_commit.msg_text.set_val(msglong)

    # log

    ui_app.pane_log.repos.on_click = on_filter_log_repo
    ui_app.pane_log.clear_btn.on_click = log_clr
    ui_app.pane_log.follow_ck.on_change = prefs_changed(CFG_LOG_FOLLOW)

    ui_app.pane_log.follow_ck.set_val(
        app.base.getbool(CFG_LOG_FOLLOW, CFG_LOG_FOLLOW_DEFAULT))

    # expert

    ui_app.pane_extralog.clear_btn.on_click = expertlog_clr
    ui_app.pane_extralog.follow_ck.on_change = prefs_changed(CFG_DEV_FOLLOW)

    ui_app.pane_extralog.follow_ck.set_val(
        app.base.getbool(CFG_DEV_FOLLOW, CFG_DEV_FOLLOW_DEFAULT))

    # only used when staring multiple time during development
    logex.handlers.clear()  # todo -> aquire lock handling

    if app.base.getbool(CFG_DEV_MODE, CFG_DEV_MODE_DEFAULT) is False:
        ui_app.main.hide_name("expert")
    else:
        # queue a incoming log message
        logex.addHandler(LogOutHandler(
            callb=logex_add))

    # prefs

    ui_app.pane_prefs.inp_open_config_folder.on_click = lambda: open_file_explorer(
        FileStat("~").join([PATH]).name)

    ui_app.pane_prefs.inp_min_text_len.set_val(app.base.getint(
        CFG_MIN_COMMIT_LENGTH, CFG_MIN_COMMIT_LENGTH_DEFAULT))
    ui_app.pane_prefs.inp_min_text_len.on_change = prefs_changed(
        CFG_MIN_COMMIT_LENGTH)

    ui_app.pane_prefs.inp_max_records_log_len.set_val(
        app.base.getint(CFG_MAX_RECORDS, CFG_MAX_RECORDS_DEFAULT))
    ui_app.pane_prefs.inp_max_records_log_len.on_change = prefs_changed(
        CFG_MAX_RECORDS)

    ui_app.pane_prefs.inp_max_records_commit_len.set_val(
        app.base.getint(CFG_MAX_COMMIT, CFG_MAX_COMMIT_DEFAULT))
    ui_app.pane_prefs.inp_max_records_commit_len.on_change = prefs_changed(
        CFG_MAX_COMMIT)

    ui_app.pane_prefs.inp_git_exe.set_val(app.base.get(CFG_GIT, get_git_exe()))
    ui_app.pane_prefs.inp_git_exe.on_change = prefs_changed(
        CFG_GIT, lambda k, curval: set_git_exe(curval))

    ui_app.pane_prefs.inp_show__changes_tab.set_val(
        app.base.getbool(CFG_SHOW_CHANGES_TAB, CFG_SHOW_CHANGES_TAB_DEFAULT))
    ui_app.pane_prefs.inp_show__changes_tab.on_change = prefs_changed(
        CFG_SHOW_CHANGES_TAB)

    def _switch_expert(x, y):
        if app.base.getbool(CFG_DEV_MODE, CFG_DEV_MODE_DEFAULT) is False:
            ui_app.main.hide_name("expert")
        else:
            ui_app.main.select_name("expert")

    ui_app.pane_prefs.inp_lbl_expert_mode.set_val(
        app.base.getbool(CFG_DEV_MODE, CFG_DEV_MODE_DEFAULT))
    ui_app.pane_prefs.inp_lbl_expert_mode.on_change = prefs_changed(
        CFG_DEV_MODE, _switch_expert)

    ui_app.pane_prefs.inp_max_records_expert_log_len.set_val(
        app.base.getint(CFG_DEV_FOLLOW_MAX, CFG_DEV_FOLLOW_MAX_DEFAULT))
    ui_app.pane_prefs.inp_max_records_expert_log_len.on_change = prefs_changed(
        CFG_DEV_FOLLOW_MAX)

    ui_app.pane_prefs.inp_max_threads.set_val(
        app.base.getint(P_THREADS, P_THREADS_DEFAULT))
    ui_app.pane_prefs.inp_max_threads.on_change = prefs_changed(
        P_THREADS)

    #

    tk_bg_bring_to_front(tk_get_root())

    #

    ui_app.set_title(VERSION)

    # update first time
    root.after(153, refresh_tracked_from_workspace)

    root.mainloop()

if __name__ == "__main__":
    run_main()