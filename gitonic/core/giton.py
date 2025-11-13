"""
    (c) 2021-2025 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""

import os
import logging
import shlex
import queue

from const import VERSION
from file import FileStat

from logs import LogOutHandler

from gitobj import GitWorkspace, GitRepo
from gitcmd import (get_git_exe, git_version, git_fetch, git_pull,
                    git_stat, git_branch, git_tag, git_commit,
                    git_push, git_push_tags, git_add, git_add_undo,
                    git_add_index_undo, git_diff, git_difftool)
from task import FuncTask

#


#


class RepoLog(object):

    repologs = {}

    @staticmethod
    def getLogHandler(reponame=None):
        nam = "repo:"
        if reponame:
            nam += reponame
        if reponame in RepoLog.repologs:
            rlog = RepoLog.repologs.get(reponame)
        else:
            rlog = RepoLog(reponame)
        return rlog

    @staticmethod
    def shutdown():
        RepoLog.repologs.clear()

    @staticmethod
    def repo_it():
        for rl in RepoLog.repologs.values():
            yield rl.name, rl.q

    # dont create instances directly
    def __init__(self, reponam):
        self.name = reponam
        self.q = queue.Queue()

        self.lh = LogOutHandler(callb=self.put_queue,
                                name=self.name).filter_on_name()

        logrepo.addHandler(self.lh)

        assert reponam not in RepoLog.repologs
        RepoLog.repologs[reponam] = self

    def __repr__(self):
        return f"{self.__class__.__name__}( {self.name} )"

    def __del__(self):
        self.remove()

    def strip(self):
        self.lh.strip()
        return self

    def remove(self):
        if self.lh in logrepo.handlers:
            logrepo.removeHandler(self.lh)

    # todo
    @staticmethod
    def remove_name(name):
        hl = list(filter(lambda x: x.name == name, logrepo.handlers))
        for h in hl:
            h.remove()

    def put_queue(self, s):
        self.q.put(s)

    @property
    def queue(self):
        return self.q

    def get_nowait(self):
        return self.q.get_nowait()

#


logex = logging.getLogger("expert")

logrepo = logging.getLogger("repo")
repolog_qu = RepoLog.getLogHandler()

#


class GitonicCmdIt(object):

    def __init__(self):
        self._stop_req = False
        self._workspace = []
        self._repo = {}

    def __repr__(self):
        return "Gitonic workspaces: " + str(self._workspace)

    def stop(self):
        self._stop_req = True

    def cont(self):
        # todo
        # remove ?
        # make sure all background tasks stopped
        self._stop_req = False

    def _stop_callb(self):
        return self._stop_req

    def version(self):
        return VERSION

    def gitversionlong(self):
        cmd = git_version()
        rc = cmd.run()
        if rc:
            raise Exception("tag", rc)
        version = "\n".join(cmd.result()).strip()
        return version

    def gitversion(self):
        version = self.gitversionlong().split()[-1]
        return version

    def get_workspaces_names(self):
        return list(self._workspace.keys())

    def workspace(self, workspace):
        fnam = FileStat(workspace).name
        if fnam in self._workspace:
            return self._workspace[fnam]

    def workspace_spec_it(self, workspace, noexists=False):

        workspace = shlex.split(workspace)

        workspace = "\n".join(workspace)
        workspace = workspace.splitlines(False)
        workspace = map(lambda x: x.strip(), workspace)

        workspace = filter(lambda x: x not in [";", ":", ","], workspace)

        workspace = filter(lambda x: len(x) > 0, workspace)

        if noexists is False:
            workspace = filter(lambda x: FileStat(
                x, prefetch=True).exists(), workspace)
            workspace = filter(lambda x: FileStat(
                x, prefetch=True).is_dir(), workspace)

        yield from workspace

    def refreshworkspace(self, workspace):

        self._repo.clear()
        self._workspace .clear()

        self._workspace = dict([(FileStat(x).name, GitWorkspace(x).refresh())
                                for x in self.workspace_spec_it(workspace)])

        return self._workspace

    def workspace_repo_it(self, wss, tracked=None):

        for d in sorted(wss.keys()):
            ws = wss[d]
            for r in sorted(ws.gits):
                if tracked is not None and r not in tracked:
                    continue
                yield r

    def get_repo(self, rnam):
        repo = None

        repo = self._repo.get(rnam)

        if repo is None:
            repo = GitRepo(rnam)
            self._repo[rnam] = repo

        return repo

    #

    def fetch_task_it(self, repo):
        logex.info("fetch_task_it", repo)

        cmd = git_fetch(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("fetch_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "fetch", cmd.result())

    def pull_task_it(self, repo):
        logex.info("pull_task_it", repo)

        cmd = git_pull(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("pull_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "pull", cmd.result())

    #

    def get_tags_task_it(self, repo):

        logex.info("get_tags_task_it", repo)

        cmd = git_tag(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("get_tags_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam,  "tags", cmd.result())

        ftcmd = FuncTask().set_name("tag").set_func(
            lambda x: repo.refresh_tags(cmd.result()))
        yield ftcmd

    def push_task_it(self, repo):
        logex.info("push_task_it", repo)

        cmd = git_push(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("push_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "push", cmd.result())

    def pushtags_task_it(self, repo):
        logex.info("pushtags_task_it", repo)

        cmd = git_push_tags(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("pushtags_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "push-tags", cmd.result())

    def commit_task_it(self, repo, message):
        logex.info("commit_task_it", repo, message)

        cmd = git_commit(repo.path, message, stopcb=self._stop_callb)
        yield cmd

        logex.info("commit_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "commit", cmd.result())

    def refresh_task_it(self, repo):
        logex.info("refresh_task_it", repo)

        cmd = git_stat(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("refresh_task_it stat", repo, cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "status", cmd.result())

        ftcmd = FuncTask().set_name("status").set_func(
            lambda x: repo.refresh_status(cmd.result()))
        yield ftcmd

        cmd = git_branch(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("refresh_task_it branch", repo, cmd.result())
        logrepo.info(reponam, "branch", cmd.result())

        ftcmd = FuncTask().set_name("branches").set_func(
            lambda x: repo.refresh_branches(cmd.result()))
        yield ftcmd

        cmd = git_tag(repo.path, stopcb=self._stop_callb)
        yield cmd

        logex.info("refresh_task_it tag", repo, cmd.result())
        logrepo.info(reponam, "tag", cmd.result())

        ftcmd = FuncTask().set_name("tags").set_func(
            lambda x: repo.refresh_tags(cmd.result()))
        yield ftcmd

    def stage_files_task_it(self, repo, files):
        logex.info("stage_files_task_it", repo, files)

        print("***add", files)

        if len(files) == 0:
            print("empty list")
            return

        # remove renamed files
        files = list(filter(lambda x: x.staged != "R", files))

        # status -> fnam
        files = list(map(lambda x: x.file, files))

        cmd = git_add(repo.path, files, stopcb=self._stop_callb)
        yield cmd

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "add", cmd.result())

    def unstage_files_task_it(self, repo, files):
        logex.info("unstage_files_task_it", repo, files)

        print("***undo add", files)

        files = list(filter(lambda x: x.staged != "R", files))

        files_m = list(filter(lambda x: x.staged != "A", files))
        files_m = list(map(lambda x: x.file, files_m))

        files_a = list(filter(lambda x: x.staged == "A", files))
        files_a = list(map(lambda x: x.file, files_a))

        logex.info("M files", files_m)
        logex.info("A files", files_a)

        # status -> fnam
        files = list(map(lambda x: x.file, files))

        if len(files) == 0:
            print("empty list")
            return

        if len(files_m) > 0:
            cmd = git_add_undo(repo.path, files_m, stopcb=self._stop_callb)
            yield cmd

        if len(files_a) > 0:
            cmd = git_add_index_undo(
                repo.path, files_a, stopcb=self._stop_callb)
            yield cmd

        logex.info("unstage_files_task_it", cmd.result())

        reponam = FileStat(repo.path).collapse()
        logrepo.info(reponam, "undo-add", cmd.result())

    def diff_files_task_it(self, repo, files):
        logex.info("diff_files_task_it", repo, files)

        if len(files) == 0:
            print("empty list")
            return

        for file in files:

            cmd = git_diff(repo.path, file.file.file, stopcb=self._stop_callb)
            yield cmd

            logex.info("diff_files_task_it result", cmd.result())

            reponam = FileStat(repo.path).collapse()
            for s in cmd.result():
                logrepo.info(reponam, s.rstrip())

    def difftool_files_task_it(self, repo, files):
        logex.info("difftool_files_task_it", repo, files)

        if len(files) == 0:
            print("empty list")
            return

        for file in files:

            # dummy task
            # todo remove
            yield FuncTask().set_name("nop").set_func()

            # todo pushdir
            cwd = os.getcwd()
            try:
                os.chdir(repo.path)
                if os.getcwd() != repo.path:
                    raise Exception("path not exist", repo.path)

                # run unattached

                args = [get_git_exe(), "difftool", file.file.file]
                rc = os.spawnvpe(os.P_NOWAIT, args[0], args, os.environ)

                logex.info("difftool_files_task_it started", args)

            except Exception as ex:
                logex.error(ex)

            os.chdir(cwd)

            logex.info("difftool_files_task_it done", repo)
