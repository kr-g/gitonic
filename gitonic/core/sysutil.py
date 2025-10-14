import sys
import os
import subprocess


def open_file_explorer(d):
    if sys.platform == "win32":
        subprocess.Popen(["start", d], shell=True)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", d])
    else:
        subprocess.Popen(["xdg-open", d])


def platform_windows():
    return sys.platform == "win32"


def platform_mac_os():
    return sys.platform == "darwin"


def platform_linux():
    return sys.platform == "linux"


def get_terminal_size():
    try:
        return os.get_terminal_size()
    except:
        pass
