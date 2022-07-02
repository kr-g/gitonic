[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Publish Python 🐍 distributions 📦 to PyPI](https://github.com/kr-g/gitonic/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/kr-g/gitonic/actions/workflows/publish-to-pypi.yml)

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


# recommended readings prior using gitonic

an introduction on how git works in general can be found in the official git documentation in section
[`Git-Basics`](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository).


# how to use

todo - documentation pending


## working with mutiple git repositories

when adding a git repo to the tracked list, and staging files (from different repositories)
a following commit command is executed on all repositories in the tracked list with the same commit message.
this is not a bug; moreover it is intened to be like that.


# hokeys 

press `ESC` key to minimize gitonic window.

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


# installation

    phyton3 -m pip install gitonic

to use git difftool, and mergetool install a 3rd party tool like 
[`meld merge`](https://meldmerge.org/)
and configure like described below


# git configuration

add a `.git-credentials` file as described here 
[`git-credentials`](https://git-scm.com/docs/git-credential-store#_storage_format)


add a `.gitconfig` file as described here
[`git-config`](https://git-scm.com/docs/git-config)
and configure for diff and merge tools


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
  - git history browser
- [`git-gui`](https://git-scm.com/docs/git-gui/)
  - a git front end


# license

gitonic is released under the following
[`LICENSE`](https://github.com/kr-g/gitonic/blob/main/LICENSE.md)
