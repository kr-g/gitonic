
# BACKLOG

- documentation
- testcases?
- revert changes / git checkout support
- git branch support
  - create
  - switch
- git tag support
- git stash support (list, show, push, pop/apply, drop, clear)
- merge tool integration
- settings tabs
  - check for installed git
  - ~~git exe configuration in settings~~
  - check for latest version of gitonic
  - 
- ~~config file for last known config~~
- gui rework
  - theme support
  - resize behavior -> expand
  - icons
  - 
- background task and event loop -> freezing gui when running git utils
  - use TkCmd also for Cmd runners
  - status bar with running background tasks overview?
  -
- refact for integration in other tools
- filter git on 'changes' tab
- rework logging
- remove print statements
- automation / external jobs
  - black PEP8 support
  - desktop integration
    - open shell at repo path
    - open file management too at repo path
- ~~history of commit texts~~
  - ~~in combo box~~
  - git log / show integration?


# OPEN ISSUES

refer to [issues](https://github.com/kr-g/gitonic/issues)


# LIMITATIONS

- ~~currently the tracked workspace is fix located under `~/repo`
  - provided in version v0.0.2~~
- difftool only works with unstaged files, no diff on already staged or 
 commited changes (same behavior as cmd-line `git difftool`)
- git credentials basic support, 
 you need to use https://git-scm.com/docs/git-credential-store.
 no separate credit store provided.
- only existing git repo's under the workspace are supported,
 as of now so support to create a new git repo. 
 use `git init`, or `git clone` manually from cmd-line
- 
 

