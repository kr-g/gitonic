"""
    (c)2021 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/pygitonic/blob/main/LICENSE.md
"""


import os
import glob

from file import FileStat, PushDir
from task import Cmd, CmdTask

GIT = "git"


join_wait = True


def git_cmd(cmdline, callb=None):
    cmd = CmdTask().set_command(f"{GIT} {cmdline}").set_callb(callb)
    cmd.start()
    if join_wait:
        cmd.join()
        assert not cmd.running()
        return cmd.popall()
    return cmd


def with_git_cmd(repo, cmd, callb=None):
    with PushDir(repo) as pd:
        return git_cmd(cmd, callb=callb)


def join_files(files, sep=" "):
    return sep.join(map(lambda x: "'" + x + "'", files))


git_version = lambda callb=None: git_cmd(f"--version", callb=callb)[0].split()[2]

git_pull = lambda repo, callb=None: with_git_cmd(repo, f"pull", callb=callb)

git_stat = lambda repo, callb=None: with_git_cmd(
    repo, f"status --porcelain", callb=callb
)

git_diff = lambda repo, file, callb=None: with_git_cmd(
    repo, f"diff {file}", callb=callb
)
git_difftool = lambda repo, file, callb=None: with_git_cmd(
    repo, f"difftool {file}", callb=callb
)

git_add = lambda repo, files, callb=None: with_git_cmd(
    repo, f"add {join_files(files)}", callb=callb
)

git_commit = lambda repo, comment, callb=None: with_git_cmd(
    repo, f"commit -m {comment} ", callb=callb
)
git_commit_porcelain = lambda repo, comment, callb=None: with_git_cmd(
    repo, f"commit --porcelain -m {comment} ", callb=callb
)

git_push = lambda repo, comment, callb=None: with_git_cmd(
    repo, f"push --porcelain", callb=callb
)
git_push_tags = lambda repo, comment, callb=None: with_git_cmd(
    repo, f"push --porcelain --tags", callb=callb
)
git_push_all = (
    lambda repo, comment, callb=None: git_push(repo, callb=callb)
    + ["---"]
    + git_push_tags(repo, callb=callb)
)

git_add_undo = lambda repo, files, callb=None: with_git_cmd(
    repo, f"restore --staged {join_files(files)}", callb=callb
)

git_checkout = lambda repo, files, callb=None: with_git_cmd(
    repo, f"checkout {join_files(files)}", callb=callb
)
git_checkout_ref = lambda repo, ref, callb=None: git_checkout(repo, [ref], callb=callb)

git_tags = lambda repo, callb=None: with_git_cmd(repo, "tag", callb=callb)
git_branches = lambda repo, callb=None: with_git_cmd(repo, "branch --all", callb=callb)
git_curbranch = lambda repo, callb=None: with_git_cmd(
    repo, "branch --show-current", callb=callb
)

git_make_tag = lambda repo, tag, callb=None: with_git_cmd(
    repo, f"tag {tag}", callb=callb
)
git_make_branch = lambda repo, branch, callb=None: with_git_cmd(
    repo, f"branch {branch}", callb=callb
)


class GitStatus(object):
    def __init__(self, mode=None, file=None):
        self.set(mode, file)

    def set(self, mode, file):
        self.mode = mode.upper() if mode else ""
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

        return self

    def from_str(self, s):
        self.set(*s.split(" "))
        return self

    def __repr__(self):
        return f"{self.__class__.__name__}('{ self.file }', '{ str(self.mode) }' )"


class GitRepo(object):
    def __init__(self, repo):
        self.path = FileStat(repo).name
        self.status = []

    def __repr__(self):
        return f"{self.__class__.__name__}('{ self.path }')"

    def refresh_status(self):
        file_status = git_stat(self.path)
        self.status.clear()
        for stat in file_status:
            gfs = GitStatus().from_str(stat)
            self.status.append(gfs)
        return self

    def stat(self, status):
        fs = FileStat(self.path).join([status.file])
        fs.stat()
        return fs


class GitWorkspace(object):
    def __init__(self, base_repo_dir="~/repo"):
        self.base_repo_dir = FileStat(base_repo_dir)
        self.gits = {}

    def __repr__(self):
        return f"{self.__class__.__name__}( { ', '.join(self.gits) } )"

    def refresh(self):
        self.gits.clear()
        gits = self.base_repo_dir.iglob("**/.git", True)
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
                lambda x: GitRepo(x),
                filter(lambda x: x.find(search_str) >= 0, self.gits),
            )
        )


#

if __name__ == "__main__":

    frepo = FileStat("~/repo")

    gws = GitWorkspace(frepo.name)
    gws.refresh()
    gws.refresh_status()

    for path, git in gws.gits.items():

        if len(git.status) > 0:
            print("---status---", path)

            for stat in git.status:
                fs = git.stat(stat)
                print(stat, "file" if fs.is_file() else "dir")
