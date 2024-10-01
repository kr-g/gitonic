"""
    (c)2021 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""


import os
import glob

from .file import FileStat, PushDir
from .task import Cmd, CmdTask
from .sysutil import platform_windows

GIT = "git.exe" if platform_windows() else "git"
BLACK = "black"


join_wait = True


def set_wait_mode(mode=True):
    global join_wait
    join_wait = mode


def set_git_exe(git_exe):
    global GIT
    GIT = git_exe


def run_cmd(cmdline, callb=None):
    cmd = CmdTask().set_command(f"{cmdline}").set_callb(callb)
    cmd.start()
    if join_wait:
        cmd.join()
        assert not cmd.running()
        return cmd.popall()
    return cmd


def git_cmd(cmdline, callb=None):
    return run_cmd(f"{GIT} {cmdline}", callb=callb)


def with_git_cmd(repo, cmd, callb=None):
    with PushDir(repo) as pd:
        return git_cmd(cmd, callb=callb)


def with_cmd(repo, cmd, callb=None):
    with PushDir(repo) as pd:
        return run_cmd(cmd, callb=callb)


def join_files(files, sep=" "):
    return sep.join(map(lambda x: "'" + x + "'", files))


def run_black(repo, files, callb=None): return with_cmd(
    repo, f"{BLACK} {join_files(files)}", callb=callb
)


def git_version(callb=None): return git_cmd(
    f"--version", callb=callb)[0].split()[2]


def git_fetch(repo, callb=None): return with_git_cmd(
    repo, f"fetch", callb=callb)


def git_pull(repo, callb=None): return with_git_cmd(repo, f"pull", callb=callb)


def git_stat(repo, callb=None): return with_git_cmd(
    repo, f"status -u --porcelain", callb=callb
)


def git_diff(repo, file, callb=None): return with_git_cmd(
    repo, f"diff {file}", callb=callb
)


def git_difftool(repo, file, callb=None): return with_git_cmd(
    repo, f"difftool {file}", callb=callb
)


def git_add(repo, files, callb=None): return with_git_cmd(
    repo, f"add {join_files(files)}", callb=callb
)


def git_commit(repo, comment, callb=None): return with_git_cmd(
    repo, f"commit -m '{comment}'", callb=callb
)


def git_commit_porcelain(repo, comment, callb=None): return with_git_cmd(
    repo, f"commit --porcelain -m '{comment}'", callb=callb
)


def git_push(repo, callb=None): return with_git_cmd(
    repo, f"push --porcelain", callb=callb)


def git_push_tags(repo, callb=None): return with_git_cmd(
    repo, f"push --porcelain --tags", callb=callb
)


git_push_all = (
    lambda repo, callb=None: git_push(repo, callb=callb)
    + ["---"]
    + git_push_tags(repo, callb=callb)
)


def git_add_undo(repo, files, callb=None): return with_git_cmd(
    repo, f"restore --staged {join_files(files)}", callb=callb
)


def git_checkout(repo, files, callb=None): return with_git_cmd(
    repo, f"checkout {join_files(files)}", callb=callb
)
def git_checkout_ref(repo, ref, callb=None): return git_checkout(
    repo, [ref], callb=callb)


def git_tags(repo, callb=None): return with_git_cmd(repo, "tag", callb=callb)


def git_branch(repo, callb=None): return with_git_cmd(
    repo, "branch", callb=callb)


def git_branch_all(repo, callb=None): return with_git_cmd(
    repo, "branch --all", callb=callb
)


def git_curbranch(repo, callb=None): return with_git_cmd(
    repo, "branch --show-current", callb=callb
)


def git_make_tag(repo, tag, callb=None): return with_git_cmd(
    repo, f"tag {tag}", callb=callb
)


def git_make_branch(repo, branch, callb=None): return with_git_cmd(
    repo, f"branch {branch}", callb=callb
)


class GitBranch(object):
    def __init__(self, current=None, bnam=None):
        self.set(current, bnam)

    def set(self, current, bnam):
        self.current = current
        self.bnam = bnam

        return self

    def from_str(self, s):
        current = s[0] == "*"
        bnam = s[2:].strip()
        self.set(current, bnam)
        return self

    def __repr__(self):
        return f"{self.__class__.__name__}('{ self.current }', '{ str(self.bnam) }' )"


class GitStatus(object):
    def __init__(self, mode=None, staged=None, file=None):
        self.set(mode, staged, file)

    def set(self, mode, staged, file):
        self.mode = mode.upper() if mode else ""
        self.staged = staged.upper() if staged else ""

        if self.staged == "R":
            oldname, newname = file.split("->", maxsplit=1)
            file = newname  # .strip()

        if file and file.startswith("\""):
            assert file.endswith("\""), "quoted string expected. " + str(file)
            file = file[1:-1]

        self.file = file
        self.state = {}

        for s, fc in [
            ("M", "modified"),
            ("A", "added"),
            ("D", "deleted"),
            ("R", "renamed"),
            ("C", "copied"),
            ("U", "updated_but_unmerged"),
            ("??", "not_in_git"),
        ]:
            comb = {f"is_{fc}": self.mode.find(s) >= 0}
            self.state.update(comb)
            self.__dict__.update(comb)

            comb = {f"is_staged_{fc}": self.staged.find(s) >= 0}
            self.state.update(comb)
            self.__dict__.update(comb)

        return self

    def has_staged(self):
        return len(self.staged) > 0

    def from_str(self, s):
        if s[:2] == "??":
            mode = "??"
            staged = ""
        else:
            staged = s[0].strip()
            mode = s[1].strip()
        file = s[3:].strip()
        self.set(mode, staged, file)
        return self

    def __repr__(self):
        return f"{self.__class__.__name__}('{ self.file }', '{ str(self.mode) }', '{ str(self.staged) }' )"


class GitRepo(object):
    def __init__(self, repo):
        self.path = FileStat(repo).name
        self.status = []
        self.branch = []
        self.current_branch = None

    def __repr__(self):
        return f"{self.__class__.__name__}('{ self.path }')"

    def refresh_status(self):
        file_status = git_stat(self.path)
        self.status.clear()

        for stat in file_status:
            gfs = GitStatus().from_str(stat)
            self.status.append(gfs)
        self.status.sort(key=lambda x: x.file)

        self.current_branch = None
        branches = git_branch(self.path)
        self.branch.clear()
        for branch in branches:
            gb = GitBranch().from_str(branch)
            self.branch.append(gb)
            if gb.current:
                self.current_branch = gb

        return self

    def stat(self, status):
        fs = FileStat(self.path).join([status.file])
        fs.stat()
        return fs

    def has_staged(self):
        return any(map(lambda x: x.has_staged(), self.status))


class GitWorkspace(object):
    def __init__(self, base_repo_dir="~/repo"):
        base_repo_dir = base_repo_dir.split(";")
        base_repo_dir = map(lambda x: x.strip(), base_repo_dir)
        base_repo_dir = map(lambda x: self._strip_quotes(x), base_repo_dir)
        base_repo_dir = map(lambda x: x.strip(), base_repo_dir)
        base_repo_dir = filter(lambda x: len(x) > 0, base_repo_dir)
        base_repo_dir = filter(lambda x: FileStat(x).exists(), base_repo_dir)

        self.base_repo_dir = [FileStat(x) for x in base_repo_dir]
        self.gits = {}

    def __repr__(self):
        return f"{self.__class__.__name__}( { ', '.join(self.gits) } )"

    def _strip_quotes(self, s):
        for quo in ["\"", "\'"]:
            if s.startswith(quo) and s.endswith(quo):
                return s[1:-1]
        return s

    def refresh(self):
        self.gits.clear()
        for repodir in self.base_repo_dir:
            gits = repodir.iglob("*/.git", True)
            for g in gits:
                path = g.dirname()
                git = GitRepo(path)
                self.gits[path] = git

    def refresh_status(self):
        for _, git in self.gits.items():
            git.refresh_status()

    def find(self, search_str):
        return list(
            map(
                lambda x: self.gits[x],
                filter(lambda x: x == search_str, self.gits),
            )
        )
