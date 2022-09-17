[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# gitonic 

gitonic simplifies working with multiple git repositories.

gitonic comes with an easy to use Tkinter GUI.

there is also a plugin for thonny 
[`thonny-gitonic`](https://github.com/kr-g/thonny-gitonic) 


# what's new ?

Check
[`CHANGELOG`](https://github.com/kr-g/gitonic/blob/main/CHANGELOG.md)
for latest ongoing, or upcoming news.


# limitations

Check 
[`BACKLOG`](https://github.com/kr-g/gitonic/blob/main/BACKLOG.md)
for open development tasks and limitations.

IMPORTANT:

`gitonic` interacts with `git` just like starting in bash / commandline.
at the present time there is _no_additional_ error checking. 
this must be done by checking the log tab manually where all cmdline output goes.


# recommended readings prior using gitonic

an introduction on how git works in general can be found in the official git documentation in section
[`Git-Basics`](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository).


# how to use

todo - documentation pending


## working with mutiple git repositories

when adding a git repo to the tracked list, and staging files (from different repositories)
a following commit command is executed on all repositories in the tracked list with the same commit message.
this is not a bug; moreover it is intened to be like that.


# hotkeys 

following list contains all hotkeys:

| key | action |
|---|---|
| Esc | minimize |
| Control-p | pull all tracked gits |
| F1 | refresh all in changed files view |
| F2 | select all in changed files view |
| F3 | un-select all in changed files view |
| Alt-a | stage file(s) in git |
| Alt-q | un-stage file(s) in git |
| Alt-w | diff file(s) |
| Alt-d | difftool file(s) |
| Alt-f | auto format file(s) with `black` PEP08 |
| Alt-x | commit file(s) |
| Alt-s | push git(s) |
| Alt-e | commit and push git(s), like pressing Alt-x and Alt-s |

HINT:

if not responding to a hotkey, make sure that CapsLock is disabled


# file status staged / unstaged 

the file status is the same as when calling 
[`git status --porcelain`](https://git-scm.com/docs/git-status#_output)


| status | comment |
|---|---|
| M | modified |
| A | added |
| D | deleted |
| R | renamed |
| C | copied |
| U | updated but unmerged |
| ?? | not in git |


# platform

tested on python3, and linux


# development status

alpha state, use on your own risk!!!


# installation

    phyton3 -m pip install gitonic

to use git difftool, and mergetool install a 3rd party tool like 
[`meld merge`](https://meldmerge.org/)
and configure like described below


## installation on raspberry pi, or fedora

when during startup an error is thrown, such as:

    from PIL import Image, ImageTk, ImageDraw, ImageFont
    ImportError: cannot import name 'ImageTk' from 'PIL' (/usr/lib64/python3.10/site-packages/PIL/__init__.py)

here it is required to install imagetk in addtion 

    # debian ubuntu etc
    sudo apt-get install python3-pil python3-pil.imagetk

    # fedora
    sudo yum install python3-pillow python3-pillow-tk


# git configuration

add a `.git-credentials` file as described here 
[`git-credentials`](https://git-scm.com/docs/git-credential-store#_storage_format)


add a `.gitconfig` file as described here
[`git-config`](https://git-scm.com/docs/git-config)
and configure for diff and merge tools. 
NOTE: you need to install the diff-tool e.g. [`meld merge`](https://meldmerge.org/) manually, 
if meld is not installed pressing the button will have no effect.


    [user]
        name = your name
        email = you@email.tld
        
    [credential]
        helper = store

    [diff]
        tool = meld
    [difftool]
        prompt = false
    [difftool "meld"]
        cmd = meld "$LOCAL" "$REMOTE"

    [merge]
        tool = meld
    [mergetool "meld"]
        # Choose one of these 2 lines (not both!) 
        # cmd = meld "$LOCAL" "$MERGED" "$REMOTE" --output "$MERGED"
        cmd = meld "$LOCAL" "$BASE" "$REMOTE" --output "$MERGED"


# additional notes 

the following tools are part of the standard git distribution 

- [`gitk`](https://git-scm.com/docs/gitk)
git history browser
- [`git-gui`](https://git-scm.com/docs/git-gui/)
a git front end

other gui-clients are listed on [`git-scm`](https://git-scm.com/downloads/guis)


# internals

following files are used:

|file|description|
|---|---|
|~/.gitonic/commit.json|the last commit messages show in the combo box|
|~/.gitonic/tracked.json|tracked git repositories|
|~/.gitonic/config.json|configuration settings|
|~/.gitonic/socket|internal use|


HINT:
crash after configuration change can be resolved by changing the setting manually in `config.json`, or delete the config file to fall back to the defaults


# license

gitonic is released under the following
[`LICENSE`](https://github.com/kr-g/gitonic/blob/main/LICENSE.md)


