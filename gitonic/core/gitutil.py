"""
    (c) 2021-2023 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""


# import os
# import sys
# from operator import xor

# from file import PushDir
# from sysutil import platform_windows
# from threading import Thread, Event
# import asyncio

# from gitcore import GitBranch, GitStatus, GitRepo, GitWorkspace, GIT

# from proc import run_command, Listener, ResultListenerQueue, StopSig, SpawnRunner
# from proc import ResultListenerQueue as CmdResult


# class AsyncBackendThread(Thread):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.config()

#     def config(self, stop_sig=None, timeout=50, grace_period=500):
#         if stop_sig is None:
#             stop_sig = Event()
#         self.stop_sig = stop_sig
#         self.timeout = timeout
#         self.grace_period = grace_period
#         self.eloop = asyncio.new_event_loop()
#         self.cnt = 0
#         return self

#     async def _loop(self):
#         print("backend running")
#         while True:
#             self.cnt += 1
#             await asyncio.sleep(self.timeout/1000)
#             rc = self.stop_sig.is_set()
#             if rc:
#                 break
#         self.quit_all(False)
#         print("backend stopping")

#     def stop_all(self):
#         self.stop_sig.set()

#     def quit_all(self, grace=True):
#         if self.stop_sig.is_set() is False:
#             self.stop_sig.set()
#             grace = True
#         if grace:
#             asyncio.sleep(self.grace_period)

#     def create_task(self, coro):
#         task = self.eloop.create_task(coro)

#     def run(self):
#         print("backend started")
#         self.eloop.run_until_complete(self._loop())
#         print("backend stoped")


# async def add_loop():
#     print("add loop start")
#     while True:
#         await asyncio.sleep(0)
#         if asyncbackend.stop_sig.wait(5):
#             break
#         print("***looping***")
#     print("add loop done")


# asyncbackend = AsyncBackendThread()
# asyncbackend.start()

# asyncbackend.create_task(add_loop())


# class CmdThread(Thread):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.stopsig = None
#         self.proc = None
#         self.config(None)

#     def config(self, cmd, callback=None, cwd=".", stop_sig=None):
#         self.cmd = cmd
#         self.callback = callback
#         self.cwd = cwd
#         self.stopsig = stop_sig
#         return self

#     def stop(self):
#         if self.stopsig:
#             self.stopsig.stop()
#         super().stop()

#     def run(self):
#         assert self.cmd, "no command"

#         print("thread run")

#         with PushDir(self.cwd) as pd:

#             cfg = Config()
#             cfg.cmd = self.cmd
#             cfg.callback = self.callback
#             cfg.rstrip = True
#             cfg.decode = True

#             # this calls a different proccess
#             # collects the output, calls listener
#             # and checks stop_signal

#             runner = SpawnRunner().run_ctx(stop_sig=self.stopsig, config=cfg)

#             runner = runner.start()
#             # this returns after start called -> run
#             self.proc = runner.proc

#         print("thread stop")


# class Config(object):
#     def __repr__(self):
#         return str(self.__dict__)


# class Gitonic(object):
#     def __init__(self, config):
#         self.config = config
#         self.workspace = GitWorkspace(base_repo_dir=self.config.base_repo_dir)

#     def __repr__(self):
#         return str(self.__dict__)

#     def refresh_workspace(self):
#         self.workspace.refresh()

#     def run_git_cmd(self, repo, cmd, listener=None, auto_status=True, stop_sig=None):
#         if listener is None:
#             listener = []
#         gres = CmdResult(listener=listener)
#         t = CmdThread().config(cmd=f"{self.config.git_cmd} {cmd}",
#                                callback=gres.add, cwd=repo.path, stop_sig=stop_sig)
#         t.start()
#         t.join()
#         assert t.proc.returncode in [
#             0, None], f"failed with { t.proc.returncode }"

#         if auto_status:
#             self.refresh_git_status(repo)

#         return gres

#     def refresh_git(self, repo, listener=[]):
#         self.refresh_git_status(repo, listener=listener)
#         self.refresh_git_branch(repo, listener=listener)
#         self.refresh_git_tag(repo, listener=listener)

#     def refresh_git_status(self, repo, listener=[]):

#         untracked = self.config.__dict__.get("untracked", "normal")

#         gres = CmdResult(listener=listener)
#         t = CmdThread().config(
#             cmd=f"{self.config.git_cmd} status -u{untracked} --porcelain", callback=gres.add, cwd=repo.path
#         )
#         t.start()
#         t.join()
#         assert t.proc.returncode in [
#             0, None], f"failed with { t.proc.returncode }"

#         repo.refresh_status(iter(gres))

#     def refresh_git_branch(self, repo, listener=[]):

#         gres = CmdResult(listener=listener)
#         t = CmdThread().config(
#             cmd=f"{self.config.git_cmd} branch", callback=gres.add, cwd=repo.path)
#         t.start()
#         t.join()
#         assert t.proc.returncode in [
#             0, None], f"failed with { t.proc.returncode }"
#         repo.refresh_branches(iter(gres))

#     def refresh_git_tag(self, repo, listener=[]):

#         gres = CmdResult(listener=listener)
#         t = CmdThread().config(
#             cmd=f"{self.config.git_cmd} tag", callback=gres.add, cwd=repo.path)
#         t.start()
#         t.join()
#         assert t.proc.returncode in [
#             0, None], f"failed with { t.proc.returncode }"
#         repo.refresh_tags(iter(gres))

#     def clone_git(self, remote, fnam=None, listener=[]):

#         if fnam is None:
#             fnam = os.path.basename(remote)
#             fnam, _ = os.path.splitext(fnam)

#         gres = CmdResult(listener=listener)
#         t = CmdThread().config(cmd=f"{self.config.git_cmd} clone -v --progress {remote} {fnam}",
#                                callback=gres.add, cwd=self.workspace.base_repo_dir.name)
#         t.start()
#         t.join()
#         assert t.proc.returncode in [
#             0, None], f"failed with { t.proc.returncode }"

#         # add and refresh the repo
#         fnam = os.path.join(self.workspace.base_repo_dir.name, fnam)
#         repo = GitRepo(fnam)
#         self.workspace.gits[fnam] = repo
#         self.refresh_git(repo)

#         return gres, repo

#     def init_git(self, fnam, listener=[]):

#         gres = CmdResult(listener=listener)
#         t = CmdThread().config(cmd=f"{self.config.git_cmd} init {fnam}",
#                                callback=gres.add, cwd=self.workspace.base_repo_dir.name)
#         t.start()
#         t.join()
#         assert t.proc.returncode in [
#             0, None], f"failed with { t.proc.returncode }"

#         # add and refresh the repo
#         fnam = os.path.join(self.workspace.base_repo_dir.name, fnam)
#         repo = GitRepo(fnam)
#         self.workspace.gits[fnam] = repo
#         self.refresh_git(repo)

#         return gres, repo

#     def join_files(self, files, sep=" "):
#         return sep.join(map(lambda x: "'" + x + "'", files))

#     def stage(self, repo, files, listener=[]):
#         files = self.join_files(files)
#         cmd = f"add {files}"
#         gres = self.run_git_cmd(repo, cmd, listener=listener)
#         return gres

#     def unstage(self, repo, files, listener=[]):
#         files = self.join_files(files)
#         cmd = f"restore --staged {files}"
#         gres = self.run_git_cmd(repo, cmd, listener=listener)
#         return gres

#     def pull(self, repo, listener=[]):
#         cmd = f"pull -v"
#         gres = self.run_git_cmd(repo, cmd, listener=listener)
#         return gres

#     def fetch(self, repo, listener=[]):
#         cmd = f"fetch -v"
#         gres = self.run_git_cmd(repo, cmd, listener=listener)
#         return gres

#     def commit(self, repo, comment, listener=[]):
#         porcelain = "--porcelain"
#         porcelain = ""
#         cmd = f"commit -m '{comment}' {porcelain}"
#         gres = self.run_git_cmd(
#             repo, cmd, listener=listener, auto_status=False)
#         return gres

#     def push(self, repo, listener=[], push_all=True, push_tags=False):
#         assert xor(push_all, push_tags), "only one push mode supported"
#         push_all = "--all" if push_all else ""
#         push_tags = "--tags" if push_tags else ""
#         cmd = f"push --porcelain {push_all} {push_tags}"
#         gres = self.run_git_cmd(
#             repo, cmd, listener=listener, auto_status=False)
#         return gres

#     def diff(self, repo, file, listener=[], diff_tool=True):
#         diff_tool = "tool" if diff_tool else ""
#         cmd = f"diff{diff_tool} {file}"
#         gres = self.run_git_cmd(
#             repo, cmd, listener=listener, auto_status=False)
#         return gres

#     def tag(self, repo, tag_nam, listener=[]):
#         cmd = f"tag {tag_nam}"
#         gres = self.run_git_cmd(
#             repo, cmd, listener=listener, auto_status=False)
#         return gres


# cfg = Config()
# cfg.git_cmd = GIT
# cfg.base_repo_dir = "~/repo"
# # cfg.untracked = "all"

# gt = Gitonic(cfg)
# gt.refresh_workspace()

# repo = gt.workspace.gits["/home/benutzer/repo/misc"]
#
# gt.refresh_git(repo)
#
# gres = gt.stage(repo, ["gitsync/sync.py"], listener=[print])
# gres = gt.unstage(repo, ["gitsync/sync.py"], listener=[print])
#
# gres = gt.fetch(repo, listener=[print])
# gres = gt.pull(repo, listener=[print])
#
#
# gres = gt.commit(repo, "small things", listener=[print])
#
# gres = gt.push(repo, listener=[print])
#
# print("***")
#
# gres = gt.diff(repo, "gitsync/sync.py", diff_tool=False, listener=[print])


# gres = gt.clone_git("https://github.com/hreikin/tkintermd.git",
#                     fnam="tt", listener=[print])

# gres = gt.init_git( fnam="tt2", listener=[print])


#
# def git_cmd(cmdline, callb=None):
#     return run_cmd(f"{GIT} {cmdline}", callb=callb)
#
#
# def with_git_cmd(repo, cmd, callb=None):
#     with PushDir(repo) as pd:
#         return git_cmd(cmd, callb=callb)
#
#
# def with_cmd(repo, cmd, callb=None):
#     with PushDir(repo) as pd:
#         return run_cmd(cmd, callb=callb)
#
#
# def join_files(files, sep=" "):
#     return sep.join(map(lambda x: "'" + x + "'", files))
#
#
# def git_version(callb=None): return git_cmd(
#     f"--version", callb=callb)[0].split()[2]
#
#
# def git_fetch(repo, callb=None): return with_git_cmd(
#     repo, f"fetch", callb=callb)
#
#
# def git_pull(repo, callb=None): return with_git_cmd(repo, f"pull", callb=callb)
#
#
# def git_stat(repo, callb=None): return with_git_cmd(
#     repo, f"status -u --porcelain", callb=callb
# )
#
#
# def git_diff(repo, file, callb=None): return with_git_cmd(
#     repo, f"diff {file}", callb=callb
# )
#
#
# def git_difftool(repo, file, callb=None): return with_git_cmd(
#     repo, f"difftool {file}", callb=callb
# )
#
#
# def git_add(repo, files, callb=None): return with_git_cmd(
#     repo, f"add {join_files(files)}", callb=callb
# )
#
#
# def git_commit(repo, comment, callb=None): return with_git_cmd(
#     repo, f"commit -m '{comment}'", callb=callb
# )
#
#
# def git_commit_porcelain(repo, comment, callb=None): return with_git_cmd(
#     repo, f"commit --porcelain -m '{comment}'", callb=callb
# )
#
#
# def git_push(repo, callb=None): return with_git_cmd(
#     repo, f"push --porcelain", callb=callb)
#
#
# def git_push_tags(repo, callb=None): return with_git_cmd(
#     repo, f"push --porcelain --tags", callb=callb
# )
#
#
# git_push_all = (
#     lambda repo, callb=None: git_push(repo, callb=callb)
#     + ["---"]
#     + git_push_tags(repo, callb=callb)
# )
#
#
# def git_add_undo(repo, files, callb=None): return with_git_cmd(
#     repo, f"restore --staged {join_files(files)}", callb=callb
# )
#
#
# def git_checkout(repo, files, callb=None): return with_git_cmd(
#     repo, f"checkout {join_files(files)}", callb=callb
# )
# def git_checkout_ref(repo, ref, callb=None): return git_checkout(
#     repo, [ref], callb=callb)
#
#
# def git_tags(repo, callb=None): return with_git_cmd(repo, "tag", callb=callb)
#
#
# def git_branch(repo, callb=None): return with_git_cmd(
#     repo, "branch", callb=callb)
#
#
# def git_branch_all(repo, callb=None): return with_git_cmd(
#     repo, "branch --all", callb=callb
# )
#
#
# def git_curbranch(repo, callb=None): return with_git_cmd(
#     repo, "branch --show-current", callb=callb
# )
#
#
# def git_make_tag(repo, tag, callb=None): return with_git_cmd(
#     repo, f"tag {tag}", callb=callb
# )
#
#
# def git_make_branch(repo, branch, callb=None): return with_git_cmd(
#     repo, f"branch {branch}", callb=callb
# )
#
