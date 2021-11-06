import sys
import subprocess


def open_file_explorer(d):
    if sys.platform == "win32":
        subprocess.Popen(["start", d], shell=True)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", d])
    else:
        subprocess.Popen(["xdg-open", d])
