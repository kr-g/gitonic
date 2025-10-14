#!/usr/bin/env python3

# import os
# import sys
# import time

import logging

from const import CFG_WORKSPACE, CFG_WORKSPACE_DEFAULT, P_THREADS, P_THREADS_DEFAULT, COM_SHORT, COM_LONG, CFG_GIT
from configs import baseconf, trackedconf, commitconf, formatterconf, contextconf
from file import FileStat

from logs import LogOutHandler

from gitcmd import set_git_exe, get_git_exe, git_diff, git_difftool

from task import FuncTask
from giton import GitonicCmdIt
from runr import CmdRunner, RepoTaskRunner, PoolTaskRunner


#

logex = logging.getLogger("expert")
logrepo = logging.getLogger("repo")

#


class RepoRef(object):
    def __init__(self, idx, repo, file):
        self.idx = idx
        self.repo = repo
        self.file = file
        self.sel = False

    def __repr__(self):
        return f"{self.__class__.__name__}( {'*' if self.sel else '-'} {self.idx} {self.file.get_str()} {FileStat.collapseuser(self.repo.path)} {self.file.file} )"

#


class GitonicApp(object):
    def __init__(self):
        self.refs = []

        self.refresh_config()
        self.refresh_workspace()
        self.refresh_tracked()
        self.refresh_commit()
        self.refresh_formatter()

        self.gtonic = GitonicCmdIt()

    def refresh_config(self):
        self.base = baseconf.load()
        set_git_exe(baseconf.get(CFG_GIT, get_git_exe()))

    def set_git_exe(self, gexe):
        baseconf.set_val(CFG_GIT, gexe)
        set_git_exe(gexe)

    def refresh_formatter(self):
        self.formatter = formatterconf.load()

    def refresh_context(self):
        self.contextopts = contextconf.load()

    def refresh_workspace(self):
        self.wsprop = self.base.get(CFG_WORKSPACE, CFG_WORKSPACE_DEFAULT)

    def refresh_tracked(self):
        # todo ...
        self.tracked = trackedconf.load()
        self.tracked_short = sorted(list(
            map(lambda x: FileStat.collapseuser(x), self.tracked.conf)))
        # print("refresh", self.tracked.conf)

    def save_tracked(self, fnams):
        self.tracked.conf = [FileStat(x).name for x in fnams]
        self.tracked_short = sorted(list(
            map(lambda x: FileStat.collapseuser(x), self.tracked.conf)))
        # todo save
        logex.info("save", self.tracked.conf)
        self.tracked.save()

    def get_tracked(self):
        return self.tracked.conf

    def refresh_commit(self):
        self.messages = commitconf.load()

    #

    def get_conf_git(self):
        return self.base.get(CFG_WORKSPACE, CFG_WORKSPACE_DEFAULT)
    #

    def workspace_all_repo_iter(self):
        wss = self.gtonic.refreshworkspace(self.wsprop)
        allws = self.gtonic.workspace_repo_it(wss, )
        yield from allws

    #

    def _iter_refs(self, ref_spec):
        mi = 1
        mx = len(self.refs)
        for x in ref_spec.split():
            rr = x.split("-")
            if len(rr) > 2:
                rr = rr[0:2]
            if len(rr) == 1:
                rr = [rr[0], rr[0]]
            l = int(rr[0] if len(rr[0]) > 0 else mi)
            h = int(rr[1] if len(rr[1]) > 0 else mx)

            # assert l >= mi
            # assert h <= mx

            if l == h:
                yield l
            else:
                yield from range(l, h+1)

    def reset_refs(self):
        self.refs.clear()

    def sort_refs(self):
        self.refs.sort(key=lambda x: (x.repo.path, x.file.file))
        for i, x in enumerate(self.refs):
            x.idx = i + 1

    def sel_refs(self, mode, ref_spec):
        for i in self._iter_refs(ref_spec):
            try:
                self.refs[i-1].sel = mode
            except:
                logex.warn("sel_refs invalid selection", i)
        return self.refs

    #

    def _iter_all_repos(self):
        wss = self.gtonic.refreshworkspace(self.wsprop)
        allws = self.gtonic.workspace_repo_it(wss, self.get_tracked())
        yield from allws

    #

    def _make_task(self, repo_func_it):
        for rnam in self._iter_all_repos():
            repo = self.gtonic.get_repo(rnam)
            logex.info("make-task", repo)
            yield RepoTaskRunner(repo, repo_func_it(repo))

    def _make_runner(self, taskspec):
        maxthreads = baseconf.getint(P_THREADS, P_THREADS_DEFAULT)
        logex.info("maxthreads", maxthreads)

        pool = PoolTaskRunner(self._make_task(taskspec), maxthreads=maxthreads)

        def poolrun():

            rc = pool.loop()
            return rc

        return poolrun

    #


class GitCmd(CmdRunner):
    def __init__(self, app):
        CmdRunner.__init__(self)
        self.app = app
        self.runner = [self.runcmd]

    def setup(self):
        logex.info("git cmd", self.__class__.__name__)
        return self

    def loop(self):
        if len(self.runner) == 0:
            return
        rc = self.runner[0]()
        if rc:
            return True
        self.runner.pop(0)
        return len(self.runner) > 0

    def runcmd(self):
        pass

    def add(self, runner, pos=-1):
        if pos < 0:
            self.runner.append(runner)
        else:
            self.runner.insert(pos, runner)
        return self

#


class FetchCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()

        def task_it(repo):

            logex.info("fetch task_it", repo)

            yield from self.app.gtonic.fetch_task_it(repo)

            ftcmd = FuncTask().set_name("fetch nop").set_func()
            yield ftcmd

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))

        return self


class PullCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()

        def task_it(repo):

            logex.info("pull task_it", repo)

            yield from self.app.gtonic.pull_task_it(repo)

            ftcmd = FuncTask().set_name("pull nop").set_func()
            yield ftcmd

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))

        return self


#


class CommitMessageCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        self.messages = self.app.refresh_commit()
        return self

    def top(self):
        if len(self.app.messages) > 0:
            return self.app.messages.conf[0][COM_SHORT], self.app.messages.conf[0][COM_LONG]
        return "", ""

    def as_list(self):
        return list(map(lambda x: (x[COM_SHORT], x[COM_LONG]), self.app.messages.conf))

    def as_shortlist(self):
        return list(map(lambda x: x[COM_SHORT], self.app.messages.conf))

    def push(self, short, long):
        el = {COM_SHORT: short, COM_LONG: long}
        nl = list(filter(lambda x: x != el, self.app.messages.conf))

        self.app.messages.conf = [el, *nl]

        return self.app.messages.conf

    def cut_to(self, maxlength=10):
        self.app.messages.conf = self.app.messages.conf[:maxlength]

    def save(self):
        self.app.messages.save()


class RefreshCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        self.app.reset_refs()

        def add_refs(repo):
            if repo.has_staged():
                logex.info("-", FileStat.collapseuser(repo.path))
                for gf in repo.status:
                    self.app.refs.append(
                        RepoRef(len(self.app.refs)+1, repo, gf))
                    logex.info(">", gf, repo)
                    logex.info(">", str(self.app.refs[-1]))

        def task_it(repo):
            yield from self.app.gtonic.refresh_task_it(repo)

            ftcmd = FuncTask().set_name("add refs").set_func(
                lambda x: add_refs(repo))
            yield ftcmd

            # ftcmd = FuncTask().set_name("sort refs").set_func(
            #     lambda x: self.app.sort_refs())
            # yield ftcmd

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))

        return self


class CommitCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()

        short, long = CommitMessageCmd(self.app).setup().top()
        logex.info("CommitCmd", "short", short, "long", long)

        message = short
        if len(long) > 0:
            message += "\n" * 2 + long

        def task_it(repo):
            yield from self.app.gtonic.commit_task_it(repo, message)

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))
        return self

    def config_with_msg(self, short, long):
        self.short = short
        self.long = long

        cmd = CommitMessageCmd(self.app).setup()
        cmd.push(short, long)

        return self


class PushCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        task_spec = self.app.gtonic.push_task_it
        self.add(self.app._make_runner(task_spec))
        return self


class PushTagsCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        task_spec = self.app.gtonic.pushtags_task_it
        self.add(self.app._make_runner(task_spec))
        return self


class GetTagsCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        task_spec = self.app.gtonic.get_tags_task_it
        self.add(self.app._make_runner(task_spec))
        return self


class StageFileCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        self.selfiles = list(filter(lambda x: x.sel, self.app.refs))

        def task_it(repo):

            repofiles = list(
                filter(lambda x: x.repo.path == repo.path, self.selfiles))

            repofiles = list(map(lambda x: x.file.file, repofiles))

            if len(repofiles) == 0:
                yield FuncTask().set_name("nop").set_func()
                return

            yield from self.app.gtonic.stage_files_task_it(repo, repofiles)

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))
        return self


class UnstageFileCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def setup(self):
        super().setup()
        self.selfiles = list(filter(lambda x: x.sel, self.app.refs))

        def task_it(repo):

            repofiles = list(
                filter(lambda x: x.repo.path == repo.path, self.selfiles))

            # ref -> status
            repofiles = list(map(lambda x: x.file, repofiles))

            if len(repofiles) == 0:
                yield FuncTask().set_name("nop").set_func()
                return

            yield from self.app.gtonic.unstage_files_task_it(repo, repofiles)

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))
        return self


class DiffFileCmd(GitCmd):
    def __init__(self, app):
        GitCmd.__init__(self, app)

    def set_sel_files(self, sel):
        self.sel = sel
        return self

    def _diffnam(self):
        return "diff"

    def _diff(self):
        return self.app.gtonic.diff_files_task_it

    def setup(self):
        super().setup()
        self.selfiles = [self.app.refs[x] for x in self.sel]

        logex.info(self._diffnam(), self.selfiles)

        def task_it(repo):

            repofiles = list(
                filter(lambda x: x.repo.path == repo.path, self.selfiles))

            logex.info(self._diffnam() + " files", repo, repofiles)

            if len(repofiles) == 0:
                yield FuncTask().set_name("nop").set_func()
                return

            yield from self._diff()(repo, repofiles)

        task_spec = task_it
        self.add(self.app._make_runner(task_spec))
        return self


class DiffToolFileCmd(DiffFileCmd):
    def __init__(self, app):
        DiffFileCmd.__init__(self, app)

    def _diffnam(self):
        return "difftool"

    def _diff(self):
        return self.app.gtonic.difftool_files_task_it
