import platform
import sys
import os
import importlib
import re

# import setuptools


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\\s*=\\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


def load_requirements():
    with open("requirements.txt") as f:
        lines = f.readlines()
        lines = map(lambda x: x.strip(), lines)
        lines = filter(lambda x: len(x) > 0, lines)
        lines = filter(lambda x: x[0] != "#", lines)
        return list(lines)


def get_scripts(projectname):
    console_scripts = []
    gui_scripts = []

    try:
        mod = importlib.import_module(f"{projectname}.__main__")
        if "main_func" in dir(mod):
            console_scripts = [
                f"{projectname} = {projectname}.__main__:main_func",
            ]
        if "gui_func" in dir(mod):
            gui_scripts = [
                f"{projectname}-ui = {projectname}.__main__:gui_func",
            ]
    except:
        print("no scripts found", file=sys.stderr)
        raise Exception()

    entry_points = {
        "console_scripts": console_scripts,
        "gui_scripts": gui_scripts,
    }

    return entry_points


pyver = platform.python_version_tuple()[:2]
pyversion = ".".join(pyver)
python_requires = f">={pyversion}"

projectname = find_projectname()

file = os.path.join(projectname, "const.py")
version = find_version(file)

install_requires = load_requirements()

entry_points = get_scripts(projectname)
