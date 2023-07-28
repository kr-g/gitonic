[![PEP-08](https://img.shields.io/badge/code%20style-PEP08-green.svg)](https://www.python.org/dev/peps/pep-0008/)


you are reading VERSION = "v0.0.12-rc0", 
read latest version [DOCS](https://github.com/kr-g/gitonic/blob/v0.0.11/README.md) 


# gitonic 

gitonic simplifies working with multiple git repositories.


gitonic comes with an easy to use Tkinter GUI.

there is also a plugin for thonny 
[`thonny-gitonic`](https://github.com/kr-g/thonny-gitonic) 


# background 

where software components/ artefacts are stored in multiple repositories 
separately gitonic helps to keep track


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
at the present time there is **no additional** error checking. 
this must be done by checking the log tab manually where all cmdline output goes.


# recommended readings prior using gitonic

an introduction on how git works in general can be found in the official git documentation in section
[`Git-Basics`](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository).

another very good book 
[`progit2`](https://github.com/progit/progit2)
can be downloaded from the official github project page.
under [`releases`](https://github.com/progit/progit2/releases) 
are different formats such as pdf, epub ...


# how to use

todo - documentation pending


## working with mutiple git repositories

when adding a git repo to the tracked list, and staging files (from different repositories)
a following commit command is executed on **all** repositories in the tracked list with the same commit message.
this is not a bug; moreover it is intened to be like that.


# hotkeys 

following list contains all hotkeys:

| key | action |
|---|---|
| Esc | minimize the app window |
| Esc Esc | press quickly Esc twice to close the app |
| Control-p | pull all tracked gits |
| Control-Shift-p | fetch all tracked gits |
| F1 | refresh all in changed files view |
| F2 | select all in changed files view |
| F3 | un-select all in changed files view |
| F5 | select previous tab |
| F6 | select next tab |
| Alt-a | stage file(s) in git |
| Alt-q | un-stage file(s) in git |
| Alt-w | diff file(s) |
| Alt-d | difftool file(s) |
| Alt-f | auto format file(s) with `black` PEP08 |
| Alt-c | go to commit tab and clear commit message field(s) |
| Alt-x | commit file(s) |
| Alt-s | push git(s) |
| Alt-e | commit and push git(s), like pressing Alt-x and Alt-s |

HINT:

if not responding to a hotkey, make sure that CapsLock is disabled


# file status staged / unstaged 

the file status is the same as when calling 
[`git status --porcelain`](https://git-scm.com/docs/git-status#_options).
see also under [`git status output`](https://git-scm.com/docs/git-status#_output).

| status | comment |
|---|---|
| M | modified |
| A | added |
| D | deleted |
| R | renamed |
| C | copied |
| U | updated but unmerged |
| ?? | not in git |

NOTE:
`gitonic` use porcelain format version 1.


# file formatter 

it is possible to configure external formatter tools depending on the file extension.

`gitonic` will use the configuration file `~/.gitonic/formatter.json`.

the general structure is:

    {
      ".file-ext": {
        "cmd": "full-path-to-command",
        "para": [
          "%file"
        ]
      }
    }

here `para` is an array of cmd-line options passed to the formatter command
where `%file` is a placeholder and replaced by the file name

for different file extensions `gitonic` will call the formatter accordingly 
even if the selected files are of different types (extensions)


## templates for python pep08 formatters

all of the following tools are part of `gitonic` standard installation
(available as extra, see below under installation). 
choose the one what fits best for your needs.


### autopep8

[autopep8](https://github.com/hhatto/autopep8)
is a python formatter what fixes problems reported by 
[pycodestyle](https://github.com/PyCQA/pycodestyle).
pycodestyle is an official tool from python's code quality authority.

    {
      ".py": {
        "cmd": "autopep8",
        "para": [
          "-i",
          "%file"
        ]
      }
    }


### black

black is also an offical python tool, but resolves not fully to issues reported by pycodestyle.
there might be some rework required (from case to case). 
result is quite similar to autopep8 beside the list reported by pycodestyle (after formatting) 
is a bit longer comparing to autopep8 what does a better job here.

    {
      ".py": {
        "cmd": "black",
        "para": [
          "%file"
        ]
      }
    }


### yapf 

yapf (google python code formmater) is slow comparing the former tools, and re-arranges code so 
that it is reported as error by pycodestyle after formatting. 

    {
      ".py": {
        "cmd": "yapf",
        "para": [
          "-i",
          "%file"
        ]
      }
    }




# platform

tested on python3, and linux


# development status

alpha state, use on your own risk!!!


# installation

it is recommented to install gitonic into a virtual environment.
the following script will install gitonic in your home directory (linux).

    # create virtual environment 
    cd ~
    python3 -m venv gitonic

    # install gitonic with all extras
    ~/gitonic/bin/pip install gitonic[PEP08,MELD]


this script can be found here
[`install_linux.sh`](install_linux.sh)

to install just `gitonic` without the extras replace with

    # install gitonic 
    ~/gitonic/bin/pip install gitonic



to run gitonic use the script from the virtual environment directly 
(no prior venv activation required)

    ~/gitonic/bin/gitonic
    
 
it is recommented to create an alias in `.bash_aliases`. 
add the following line at the end of `.bash_aliases`

    alias gitonic=~/gitonic/bin/gitonic
    

## other installation dependencies

to use git difftool, and mergetool download and install a 3rd party tool like 
[`meld merge`](https://meldmerge.org/)
and configure like described below.

note: 

with gitonic >= v0.12.0 meld is already included in standard installation
(as extra, see also under installation) and download is obsolete when 
installed as part of gitonic. you just need to configure git then.

in case meld installation fails install into the virtual environment 

    pip install PyGObject



## installation on raspberry pi, or fedora

when during startup an error is thrown, refer to 
[installation on raspberry, fedorra](https://github.com/kr-g/gitonic/issues/6)


# git configuration

add a `.git-credentials` file as described here 
[`git-credentials`](https://git-scm.com/docs/git-credential-store#_storage_format)


add a `.gitconfig` file as described here
[`git-config`](https://git-scm.com/docs/git-config)
and configure for diff and merge tools. 
NOTE: you need to install the diff-tool e.g. 
[`meld merge`](https://meldmerge.org/) manually, 
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
|~/.gitonic/formatter.json|configuration for external formatter tools|
|~/.gitonic/socket|internal use|


HINT:
crash after configuration change can be resolved by changing the setting manually 
in `config.json`, or delete the config file to fall back to the defaults


# license

gitonic is released under the following
[`LICENSE`](https://github.com/kr-g/gitonic/blob/main/LICENSE.md)


