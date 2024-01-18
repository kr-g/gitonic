
# BACKLOG

- documentation
- testcases?
- revert changes / git checkout support
  - undo support for unstaged files
    - git restore <file>
- ~~git fetch / merge  support~~
  - ~~currently gitonic supports only pull~~
- git branch support
  - create
  - switch
- git diff rework
  - support also git diff --staged. 
  - support merge-base, refer to 
    - git difftool master...contrib
      - git merge-base contrib master 
      - git merge-base contrib master --name-only
  - diff on base of single file history
- merge tool integration
  - git commit 
  - support also git commit --amend 
- git tag support
- git stash support (list, show, push, pop/apply, drop, clear)
- support verbose output in expert mode
  - support flags -v and -vv where applicable
- settings tabs
  - check for installed git
  - ~~git exe configuration in settings~~
  - check for latest version of gitonic
  - 
- ~~config file for last known config~~
- diff-tool blocks main screen (see next)
- gui rework
  - theme support
  - resize behavior -> expand
  - ~~icons~~
  - grid layout / less floating 
  - freezing ui -> see background tasks
  -
- background task and event loop -> freezing gui when running git utils
  - use TkCmd also for Cmd runners
  - status bar with running background tasks overview?
  -
- refact for integration in other tools
- filter git on 'changes' tab
- rework logging
- ~~remove print statements in main~~
- remove print statements in tile.core
- automation / external jobs
  - ~~black PEP8 support~~
  - desktop integration
    - open shell at repo path
    - open file management too at repo path
- ~~history of commit texts~~
  - ~~in combo box~~
  - git log / show integration?
- git error handling
- switch to log tab after pull
- logging, use python logger for expert mode output
- support for .gitignore 
  - adding single files 
  - open .gitignore for editing
- execute git operations in parallel where possible
- make expert mode debugging out better (use python logging)
- 


# OPEN ISSUES

refer to [issues](https://github.com/kr-g/gitonic/issues)


# LIMITATIONS

- ~~currently the tracked workspace is fix located under `~/repo`~~
  - ~~provided in version v0.0.2~~
- difftool only works with unstaged files, no diff on already staged or 
 commited changes (same behavior as cmd-line `git difftool`)
- git credentials basic support, 
 you need to use https://git-scm.com/docs/git-credential-store.
 no separate credit store provided.
- only existing git repo's under the workspace are supported,
 as of now no support to create a new git repo. 
 use `git init`, or `git clone` manually from cmd-line
- `gitonic` interacts with `git` just like starting in bash / commandline.
at the present time there is _no_additional_ error checking. 
this must be done by checking the log tab manually where all cmdline output goes.
- at the present time the context menu only works on the underlying file (row) in the table. 
 there is no support for multiple files (selection) as of now.
 

