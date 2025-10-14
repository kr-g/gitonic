"""
    (c) 2021-2025 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/gitonic/blob/main/LICENSE.md
"""

from const import GITIGNORE
from file import FileStat
# from .sysutil import platform_windows

#


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
        return f"{self.__class__.__name__}('{self.current}', '{str(self.bnam)}' )"


class GitStatus(object):
    def __init__(self, mode=None, staged=None, file=None):
        self.set(mode, staged, file)

    def set(self, mode, staged, file):

        # mode is in working tree
        # staged is in index

        self.mode = mode.upper() if mode else ""
        self.staged = staged.upper() if staged else ""
        self.file = file
#         self.state = {}
#
#         for s, fc in [
#             ("M", "modified"),
#             ("A", "added"),
#             ("D", "deleted"),
#             ("R", "renamed"),
#             ("C", "copied"),
#             ("U", "updated_but_unmerged"),
#             ("??", "not_in_git"),
#         ]:
#             comb = {f"is_{fc}": self.mode.find(s) >= 0}
#             self.state.update(comb)
#             self.__dict__.update(comb)
#
#             comb = {f"is_staged_{fc}": self.staged.find(s) >= 0}
#             self.state.update(comb)
#             self.__dict__.update(comb)

        return self

    def has_staged(self):
        return len(self.mode) > 0 or len(self.staged) > 0

    def get_str(self):
        m = self.mode if self.mode else "-"
        s = self.staged if self.staged else "-"

        # as desscribed by git-scm
        return s + m

    def from_str(self, s):
        staged = s[0].strip()
        mode = s[1].strip()

        file = s[3:].strip()
        self.set(mode, staged, file)
        return self

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.file}', '{str(self.mode)}', '{str(self.staged)}' )"


class GitRepo(object):
    def __init__(self, repo):
        self.path = FileStat(repo).name
        self.status = []
        self.tag = []
        self.branch = []
        self.current_branch = None

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.path}')"

    def refresh_status(self, file_status):
        # file_status = git_stat(self.path)
        self.status.clear()

        for stat in file_status:
            gfs = GitStatus().from_str(stat)
            self.status.append(gfs)
        self.status.sort(key=lambda x: x.file)

    def refresh_tags(self, tags):
        self.tag = list(tags)

    def refresh_branches(self, branches):
        self.current_branch = None
        # branches = git_branch(self.path)
        self.branch.clear()
        for branch in branches:
            gb = GitBranch().from_str(branch)
            self.branch.append(gb)
            if gb.current:
                self.current_branch = gb
                # todo detached ?

        return self

    def stat(self, status):
        fs = FileStat(self.path).join([status.file])
        fs.stat()
        return fs

    def has_staged(self):
        return any(map(lambda x: x.has_staged(), self.status))

    def has_ignorefile(self):
        f = FileStat(self.path, prefetch=True).join([GITIGNORE])
        return f.exists()


class GitWorkspace(object):
    def __init__(self, base_repo_dir="~/repo"):
        self.base_repo_dir = FileStat(base_repo_dir)
        self.gits = {}

    def __repr__(self):
        return f"{self.__class__.__name__}( {', '.join(self.gits)} )"

    def repo(self, path):
        fnam = FileStat(path).name
        if fnam in self.gits:
            return self.gits[fnam]

    def refresh(self):
        self.gits.clear()
        gits = self.base_repo_dir.iglob("*/.git", True)
        for g in gits:
            path = g.dirname()
            git = GitRepo(path)
            self.gits[path] = git
        return self

#     def refresh_status(self):
#         for _, git in self.gits.items():
#             git.refresh_status()

    def find(self, search_str):
        return list(
            map(
                lambda x: self.gits[x],
                filter(lambda x: x == search_str, self.gits),
            )
        )
