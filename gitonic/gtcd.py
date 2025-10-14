#!/usr/bin/env python3

import sys
import os
import time

from core.const import CFG_TERM, CFG_TERM_DEFAULT

from core.configs import baseconf, trackedconf
from core.file import FileStat

#

baseconf.load()

tracked = trackedconf.load().conf
tracked_ex = filter(lambda x: FileStat(x, prefetch=True).is_dir(), tracked)

for i, repo in enumerate(tracked_ex):
    print("*" if i == 0 else " ", i, repo)

try:
    pos = input("change to repo [0]: ")
except:
    print("abort", file=sys.stderr)
    sys.exit(0)

try:
    pos = pos.strip()
    if len(pos) == 0:
        pos = 0
    pos = int(pos)
    if pos < 0 or pos >= len(tracked):
        raise Exception("invalid number")
    fp = tracked[pos]
except Exception as ex:
    print("err:", ex, file=sys.stderr)
    sys.exit(1)

os.chdir(fp)
sh = os.path.basename(os.environ.get("SHELL", "shell"))

term = baseconf.get(CFG_TERM, CFG_TERM_DEFAULT)

procid = os.fork()
if procid == 0:
    rc = os.system(term)
    if rc == 0:
        print(f"new {sh} changed to", FileStat.collapseuser(os.getcwd()))
else:
    # let the forked process print the message above
    # properly into the parent terminal
    time.sleep(0.35)
