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


# how to use

todo - documentation pending

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

add a `/home/benutzer/.git-credentials` file as described here 
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




# license

gitonic is released under the following
[`LICENSE`](https://github.com/kr-g/gitonic/blob/main/LICENSE.md)
