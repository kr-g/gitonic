"""
    (c)2021 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/pygitonic/blob/main/LICENSE.md
"""


import os
import glob

from file import FileStat, PushDir

GIT = "git"


def git_cmd(cmd, callb=None):
    lines = []
    with os.popen(f"{GIT} {cmd}") as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            line = line.strip()
            if callb:
                callb(line)
            else:
                lines.append(line)
    return lines


def with_git_cmd(repo, cmd, callb=None):
    with PushDir(repo) as pd:
        return git_cmd(cmd, callb=callb)


def join_files(files, sep=" "):
    return sep.join(map(lambda x: "'" + x + "'", files))


git_pull = lambda repo: with_git_cmd(repo, f"pull")

git_stat = lambda repo: with_git_cmd(repo, f"status --porcelain")

git_diff = lambda repo, file: with_git_cmd(repo, f"diff {file}")
git_difftool = lambda repo, file: with_git_cmd(repo, f"difftool {file}")

git_add = lambda repo, files: with_git_cmd(repo, f"add {join_files(files)}")

git_commit = lambda repo, comment: with_git_cmd(
    repo, f"commit --porcelain -m {comment} "
)

git_push = lambda repo, comment: with_git_cmd(repo, f"push --porcelain")
git_push_tags = lambda repo, comment: with_git_cmd(repo, f"push --porcelain --tags")
git_push_all = lambda repo, comment: git_push(repo) + ["---"] + git_push_tags(repo)

git_add_undo = lambda repo, files: with_git_cmd(
    repo, f"restore --staged {join_files(files)}"
)

git_checkout = lambda repo, files: with_git_cmd(repo, f"checkout {join_files(files)}")
git_checkout_ref = lambda repo, ref: git_checkout(repo, [ref])

git_tags = lambda repo: with_git_cmd(repo, "tag")
git_branches = lambda repo: with_git_cmd(repo, "branch --all")
git_curbranch = lambda repo: with_git_cmd(repo, "branch --show-current")

git_make_tag = lambda repo, tag: with_git_cmd(repo, f"tag {tag}")
git_make_branch = lambda repo, branch: with_git_cmd(repo, f"branch {branch}")


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
                print(stat, fs.is_file())
