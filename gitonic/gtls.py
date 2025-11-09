#!/usr/bin/env python3

# import os
# import sys
# import time

from core.logs import LogOutHandler
from gtcommon import EXPERT_LOG, REPO_LOG, logex


from core.sysutil import get_terminal_size
from core.gitonapp import (GitonicApp, RefreshCmd, PushCmd, PushTagsCmd,
                           GetTagsCmd, StageFileCmd, UnstageFileCmd, CommitMessageCmd)

from core.gitcmd import set_git_exe, get_git_exe

#


def main_func():

    app = GitonicApp()

    # app.save_tracked(['/home/benutzer/repo/allradmotorrad', '/home/benutzer/repo/autofill', '/home/benutzer/repo/dryades', '/home/benutzer/repo/espsetup', '/home/benutzer/repo/gitonic', '/home/benutzer/repo/misc', '/home/benutzer/repo/modcore', '/home/benutzer/repo/mpfshell', '/home/benutzer/repo/mpymodcore', '/home/benutzer/repo/py_play', '/home/benutzer/repo/pybicyclewheel', '/home/benutzer/repo/pyclavis',
    #                  '/home/benutzer/repo/pydataflow', '/home/benutzer/repo/pygitgrab', '/home/benutzer/repo/pytkfaicons', '/home/benutzer/repo/scanpars', '/home/benutzer/repo/smog', '/home/benutzer/repo/thonny', '/home/benutzer/repo/thonny-gitonic', '/home/benutzer/repo/xvenv', '/home/benutzer/workspace/esp-idf-st7789', '/home/benutzer/workspace/hello_world_led', '/home/benutzer/workspace/lcd', '/home/benutzer/workspace/tt'])

    # app.save_tracked(['/home/benutzer/repo/gitonic', '/home/benutzer/repo/misc', '/home/benutzer/repo/mpfshell', '/home/benutzer/repo/mpymodcore', '/home/benutzer/repo/py_play',
    #                   '/home/benutzer/repo/thonny', '/home/benutzer/repo/thonny-gitonic', '/home/benutzer/workspace/lcd', '/home/benutzer/workspace/tt'])

    # app.save_tracked([])

    cmd = RefreshCmd(app).setup().add(
        lambda: app.sort_refs() and False).complete()
    # app.sort_refs()

    # app.sel_refs(True, "1-2 4-")
    # print(app.refs)

    r = None
    for x in app.refs:
        if x.repo.path != r:
            r = x.repo.path
            print("*", r)
        print(f"{x.idx:3}", "[x]" if x.sel else "[ ]",
              x.file.get_str(), x.file.file)

    # cmd = GetTagsCmd(app).setup().complete()

    # cmd = PushCmd(app).setup().complete()
    # cmd = PushTagsCmd(app).setup().complete()

    # cmd = StageFileCmd(app).setup().complete()
    # cmd = UnstageFileCmd(app).setup().complete()

    # cmd = CommitMessageCmd(app).setup().complete()

    ver = app.gtonic.version()
    gverl = app.gtonic.gitversionlong()
    gver = app.gtonic.gitversion()

    # cmd = git_push(FileStat(rnam).name)
    # cmd.run()

    # cmd = git_push_tags(FileStat(rnam).name)
    # cmd.run()

    # term = get_terminal_size()
    # if term:
    #     print(term)

if __name__ == "__main__":
    main_func()
