

from task import Cmd, CmdTask
from sysutil import platform_windows

#


GIT = "git.exe" if platform_windows() else "git"

#


def set_git_exe(git_exe):
    global GIT
    GIT = git_exe
    # print("changed git", GIT)

#


def get_git_exe():
    return GIT


def git_cmd(repo, cmdline, callb=None, stopcb=None):
    gexe = get_git_exe()
    # print("using", gexe)
    return CmdTask() \
        .configure(callb=callb, stop_callb=stopcb) \
        .set_command(f"{gexe} -C '{repo}' {cmdline}", )


def with_git_cmd(repo, cmd, callb=None, stopcb=None):
    # with PushDir(repo):
    return git_cmd(repo, cmd, callb=callb, stopcb=stopcb)

#


def git_version(callb=None, stopcb=None):
    gexe = get_git_exe()
    # print("using", gexe)
    cmdline = "--version"
    return Cmd() \
        .configure(callb=callb, stop_callb=stopcb) \
        .set_command(f"{gexe} {cmdline}")
    # return with_git_cmd(
    #     f"--version", callb=callb)[0].split()[2]

#


def git_stat(repo, callb=None, stopcb=None):
    return with_git_cmd(
        repo, "status -u --porcelain", callb=callb, stopcb=stopcb)


def git_branch(repo, callb=None, stopcb=None):
    return with_git_cmd(
        repo, "branch", callb=callb, stopcb=stopcb)


def git_tag(repo, tagnam="", callb=None, stopcb=None):
    return with_git_cmd(
        repo, f"tag {tagnam}", callb=callb, stopcb=stopcb)

#


def join_files(files, sep=" "):
    return sep.join(map(lambda x: "'" + x + "'", files))

#


def git_diff(repo, file, callb=None, stopcb=None):
    return with_git_cmd(repo, f"diff {file}", callb=callb, stopcb=stopcb)


def git_difftool(repo, file, callb=None, stopcb=None):
    return with_git_cmd(repo, f"difftool {file}", callb=callb, stopcb=stopcb)


#

def git_add(repo, files, callb=None, stopcb=None):
    return with_git_cmd(
        repo, f"add {join_files(files)}", callb=callb, stopcb=stopcb)


def git_add_undo(repo, files, callb=None, stopcb=None):
    return with_git_cmd(
        repo, f"restore --staged {join_files(files)}", callb=callb, stopcb=stopcb)


def git_add_index_undo(repo, files, callb=None, stopcb=None):
    # for -A porcelain modes
    return with_git_cmd(
        repo, f"rm --cached {join_files(files)}", callb=callb, stopcb=stopcb)

#


def git_commit(repo, comment, callb=None, stopcb=None):
    return with_git_cmd(repo, f"commit -m '{comment}'", callb=callb, stopcb=stopcb)

#


def git_push(repo, callb=None, stopcb=None):
    return with_git_cmd(
        repo, "push --porcelain", callb=callb, stopcb=stopcb)


def git_push_tags(repo, callb=None, stopcb=None):
    return with_git_cmd(
        repo, "push --porcelain --tags", callb=callb, stopcb=stopcb)


#

def git_fetch(repo, callb=None, stopcb=None):
    return with_git_cmd(repo, "fetch", callb=callb, stopcb=stopcb)


def git_pull(repo, callb=None, stopcb=None):
    return with_git_cmd(repo, "pull", callb=callb, stopcb=stopcb)


#

# def git_commit(repo, comment, callb=None): return with_git_cmd(
#     repo, f"commit -m '{comment}'", callb=callb
# )
#
# def git_commit_porcelain(repo, comment, callb=None): return with_git_cmd(
#     repo, f"commit --porcelain -m '{comment}'", callb=callb
# )
#

# def with_cmd(repo, cmd, callb=None):
#     with PushDir(repo) as pd:
#         return run_cmd(cmd, callb=callb)
#

#
# def git_diff(repo, file, callb=None): return with_git_cmd(
#     repo, f"diff {file}", callb=callb
# )
#
# def git_difftool(repo, file, callb=None): return with_git_cmd(
#     repo, f"difftool {file}", callb=callb
# )
#
# def git_add(repo, files, callb=None): return with_git_cmd(
#     repo, f"add {join_files(files)}", callb=callb
# )
#
# def git_commit(repo, comment, callb=None): return with_git_cmd(
#     repo, f"commit -m '{comment}'", callb=callb
# )
#
# def git_commit_porcelain(repo, comment, callb=None): return with_git_cmd(
#     repo, f"commit --porcelain -m '{comment}'", callb=callb
# )
#
# def git_push(repo, callb=None): return with_git_cmd(
#     repo, f"push --porcelain", callb=callb)
#
# def git_push_tags(repo, callb=None): return with_git_cmd(
#     repo, f"push --porcelain --tags", callb=callb
# )
#
# git_push_all = (
#     lambda repo, callb=None: git_push(repo, callb=callb)
#     + ["---"]
#     + git_push_tags(repo, callb=callb)
# )
#
# def git_add_undo(repo, files, callb=None): return with_git_cmd(
#     repo, f"restore --staged {join_files(files)}", callb=callb
# )
#
# def git_checkout(repo, files, callb=None): return with_git_cmd(
#     repo, f"checkout {join_files(files)}", callb=callb
# )
# def git_checkout_ref(repo, ref, callb=None): return git_checkout(
#     repo, [ref], callb=callb)
#
# def git_branch_all(repo, callb=None): return with_git_cmd(
#     repo, "branch --all", callb=callb
# )
#
# def git_curbranch(repo, callb=None): return with_git_cmd(
#     repo, "branch --show-current", callb=callb
# )
#
# def git_make_tag(repo, tag, callb=None): return with_git_cmd(
#     repo, f"tag {tag}", callb=callb
# )
#
# def git_make_branch(repo, branch, callb=None): return with_git_cmd(
#     repo, f"branch {branch}", callb=callb
# )
#
