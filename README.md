[![PEP-08](https://img.shields.io/badge/code%20style-PEP08-green.svg)](https://www.python.org/dev/peps/pep-0008/)


you are reading VERSION = v0.19.0-develop

version v0.18.0 will come with some bigger changes.

version v0.18.0 is released for **python3.12 (fixed version)** !!!


read latest news here:

[`CHANGELOG`](https://github.com/kr-g/gitonic/blob/main/CHANGELOG.md)


older versions:

[`OLD VERSIONS`](https://github.com/kr-g/gitonic/tags)




# gitonic 

gitonic simplifies working with multiple git repositories.


gitonic comes with an easy to use Tkinter GUI.


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
| ?? | not in git. untracked |

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

where `.file-ext` is a simple file extension such as `.py`, 
or a comma separated list of extensions `.c,.h,.cpp`.
wild-cards are not supported.

where `para` is an array of cmd-line options passed to the formatter command
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

to use the same code formatter also for 
[`cython's`](https://github.com/cython/cython) 
files with extension `.pyx` change the setting to

    {
      ".py,.pyx": {
        "cmd": "autopep8",
        "para": [
          "-i",
          "%file"
        ]
      }
    }

or in case autopep8 is installed in a venv, e.g.

    {
      ".py,.pyx": {
        "cmd": "~/gitonic/.venv/bin/autopep8",
        "para": [
          "-i",
          "%file"
        ]
      }
    }



### black

black is also an offical python tool, but resolves not fully to issues reported by pycodestyle.
there might be some rework required (from case to case). 
result is quite similar to 
[autopep8](https://github.com/hhatto/autopep8)
beside the list reported by pycodestyle (after formatting) 
is a bit longer comparing to 
[autopep8](https://github.com/hhatto/autopep8)
what does a better job here.

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


## templates for c, c++ formatters

all of the following tools are NOT part of `gitonic` standard installation. 


### uncrustify

[`uncrustify`](https://github.com/uncrustify/uncrustify) 
is a code formatter for c, c++ (and other languages).

here in this config sample it is configured for extensions `.c`, `.h`, and `.cpp`.

IMPORTANT: `uncrustify` requires an additional config file, a sample can be found here
[`uncrustify.cfg`](https://github.com/uncrustify/uncrustify/blob/master/forUncrustifySources.cfg)

here in the sample the `uncrustify` config file is placed in path `~/.gitonic/uncrustify.cfg`.
make sure that it is there.

the following needs to be placed inside `~/.gitonic/formatter.json`


    ".c,.h,.cpp": {
        "cmd": "uncrustify",
        "para": [
              "-c",
              "~/.gitonic/uncrustify.cfg",
              "--replace",
              "%file",
              "--no-backup",
              "--if-changed"
        ]
    }


# custom context menu handler 

when clicking on the `changes` tab right a context memu opens offering 
to open the system file manager tool (file explorer) 
at the base git repo path or at the changed file path.

in addition it is possible to add own custom context menu entries here.
configuration is done with `~/.gitonic/contextmenu.json` file.

the general structure is:

    {
    "acontext-name": {
        "expr": "*",
        "changes-all|file|repo": [
          {
            "name": "a text $_GIT",
            "para": [
              "cmd-path",
              "whatever_param=$GIT"
            ]
          },
          {
            "name": "some other text $_PATH",
            "para": [
              "cmd-path2",
              "whatever_param=$PATH"
            ]
          },
          ...
        ]
      },
      ...
    }

where `changes-all|file|repo` is the section where the context menu should appear.
- `changes-file` is the right section where all files are listed
- `changes-repo` is the left section where all repos are listed
- `changes-all` will appear in both (left and right section)

here the variables `$GIT`, `$FILE`, `$PATH`, `$NAME`, or `$PYTHON` 
are replaced by the corrosponding path before execution. 
where `$PYTHON` expands to `sys.executable` from `gitonic` runtime.
and `$NAME` is a placeholder for `os.path.basedir`,
and `$PATH` for `os.path.dirname`.

the variables `$_GIT`, `$_FILE`, `$_PATH`, or `$_NAME` are the shorten
path specifiers with `~` replacing the users home folder.

the `expr` key contains a single file pattern, or a list of 
file patterns - when to enable the context menu. 
the file pattern is following Unix filename pattern matching.

the `workdir` key will change the current working directory before running
the command.

the `name` contains the text to display in the menu, 
and `para` the command-binary plus params as array.

the context name as such can have any value 
(as long it is unique in the structure).


below a sample `~/.gitonic/contextmenu.json` file 
for running on linux with xfce.

    {
      "term-ctx": {
        "expr": "*",
        "changes-all": [
          {
            "name": "Open Terminal at $_GIT",
            "para": [
              "xfce4-terminal",
              "--default-working-directory=$GIT"
            ]
          },
          {
            "name": "Open Terminal at $_PATH",
            "para": [
              "xfce4-terminal",
              "--default-working-directory=$PATH"
            ]
          },
          {
            "name": "Edit .gitignore at $_GIT",
            "para": [
              "xed",
              "$GIT/.gitignore"
            ]
          }
        ]
      },
      "basic-ctx": {
        "expr": "*",
        "changes-file": [
          {
            "name": "less $NAME at $_PATH",
            "para": [
              "xfce4-terminal",
              "-x",
              "less",
              "$FILE"
            ]
          },
          {
            "name": "edit $NAME at $_PATH",
            "para": [
              "xed",
              "$FILE"
            ]
          },
          {
            "name": "vi $NAME at $_PATH",
            "para": [
              "xfce4-terminal",
              "-x",
              "vi",
              "$FILE"
            ]
          }
        ]
      },
      "spyder-ctx": {
        "expr": "*.py",
        "changes-file": [
          {
            "name": "spyder python $_FILE",
            "para": [
              "~/spyder/.venv/bin/spyder",
              "$FILE"
            ]
          }
        ]
      },
      "autopep8-ctx": {
        "expr": "*.py",
        "changes-file": [
          {
            "name": "autopep8 python $_FILE",
            "para": [
              "~/repo/gitonic/.venv/bin/autopep8",
              "-i",
              "$FILE"
            ]
          }
        ]
      },
      "geany-path": {
        "expr": [
          "*.c",
          "*.cpp",
          "*.h"
        ],
        "changes-file": [
          {
            "name": "geany c $_FILE",
            "para": [
              "geany",
              "$FILE"
            ]
          }
        ]
      },
      "uncrustify-path": {
        "expr": [
          "*.c",
          "*.cpp",
          "*.h"
        ],
        "changes-file": [
          {
            "name": "uncrustify c $_FILE",
            "para": [
              "uncrustify",
              "-c",
              "~/.gitonic/uncrustify.cfg",
              "--replace",
              "$FILE",
              "--no-backup",
              "--if-changed"
            ]
          }
        ]
      },
      "git-base-tools": {
        "expr": [
          "*"
        ],
        "workdir": "$GIT",
        "changes-all": [
          {
            "name": "git push $_GIT",
            "para": [
              "git",
              "push"
            ],
            "logexpert" : true
          },
          {
            "name": "git pull $_GIT",
            "para": [
              "git",
              "pull"
            ],
            "logexpert" : true
          },
          {
            "name": "gitk $_GIT",
            "para": [
              "gitk"
            ]
          },
          {
            "name": "git gui $_GIT",
            "para": [
              "git",
              "gui"
            ]
          }
        ]
      }
    }


remark:
the sample config file provides support for opening
- terminal, in this case `xfce4-terminal`, can be replaced by e.g. `xterm` - depending on your distribution
- open file with `less`, `xed`, or `vi` - might be different with your distribution (see line above)
- `.gitignore` file for selected repo with [`xed`](https://en.wikipedia.org/wiki/Xed)
- [`spyder-ide.org`](https://spyder-ide.org/), for files matching `*.py`
- [`geany`](https://www.geany.org/), for files matching `*.c`, `*.cpp`, `*.h`
- `gitk` and `git gui` the base git tools which are automatically installed with `git`
- 


**limitation:**

at the present time the context menu only works on the underlying file (row) in the table.
there is **no** support for multiple files (selection) as of now.


# related

plugin for thonny ide 
[`thonny-gitonic`](https://github.com/kr-g/thonny-gitonic)


# platform

tested on python3, and linux


# contribution

any contribution is welcome !

please create one issue for each proposal, or merge request.


# installation

it is recommented to install gitonic into a 
[virtual environment](https://docs.python.org/3/library/venv.html).
the following script will install gitonic in your home directory (linux).


    #!/bin/bash
    
    # create virtual environment 
    
    cd ~
    python3 -m venv gitonic
    
    cd gitonic
    
    source ./bin/activate
    
    # install gitonic with all pep08 and meld
    
    pip3 install gitonic[PEP08,MELD]


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

to use git difftool, and mergetool, download and install a 3rd party tool like 
[`meld merge`](https://meldmerge.org/)
and configure like described below.

note: 

with gitonic >= v0.12.0 meld is already included in standard installation
(as extra, see also under installation) and download is obsolete when 
installed as part of gitonic. you just need to configure git then.

in case meld installation fails install into the virtual environment 

    cd ~
    ~/gitonic/bin/pip install PyGObject


### all installation options

options can be combined by `|`.
use 

    ~/gitonic/bin/pip install gitonic[*options*] 


|option|included packages|
|---|---|
| PEP08 | pycodestyle, flake8, autopep8 |
| PEP08_BLACK | pycodestyle, flake8, black |
| PEP08_FULL | pycodestyle, flake8, autopep8, black, yapf |
| MELD | meld |
| DEFAULT | pycodestyle, flake8, autopep8, meld |


## installation on raspberry pi, or fedora

when during startup an error is thrown, refer to 
[installation on raspberry, fedorra](https://github.com/kr-g/gitonic/issues/6)


# git configuration

add a `.git-credentials` file as described here 
[`git-credentials`](https://git-scm.com/docs/git-credential-store)


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
        cmd = meld --newtab "$LOCAL" "$REMOTE"

    [merge]
        tool = meld
    [mergetool "meld"]
        # Choose one of these 2 lines (not both!) 
        # cmd = meld "$LOCAL" "$MERGED" "$REMOTE" --output "$MERGED"
        cmd = meld --newtab "$LOCAL" "$BASE" "$REMOTE" --output "$MERGED"


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
|~/.gitonic/config.json|configuration settings|
|~/.gitonic/contextmenu.json|configuration for context menu on changes tab|
|~/.gitonic/formatter.json|configuration for external formatter tools|
|~/.gitonic/tracked.json|tracked git repositories|
|~/.gitonic/socket|internal use|


HINT:
crash after configuration change can be resolved by changing the setting manually 
in `config.json`, or delete the config file to fall back to the defaults


# license

gitonic is released under the following
[`LICENSE`](https://github.com/kr-g/gitonic/blob/main/LICENSE.md)

git logos from [git-scm](https://git-scm.com/downloads/logos)


# support and donations

support the further development of `gitonic` with a donation of your choice.

[support and donnations](https://github.com/kr-g/gitonic/wiki/Support)

thank you !!!

