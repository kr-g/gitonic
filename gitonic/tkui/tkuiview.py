
import sys
import os

import tkinter as tk
import tkinter.ttk as ttk

from tkuiwidg import TNLabel, TNLabelClick, TNLabelClickUrl
from tkuiwidg import TNButton, TNCheckButton, TNEntryString, TNEntryInt
from tkuiwidg import TNCombobox, TNListbox, TNScrolledText, TNTreeview, TNNotebook

#

T_SETTINGS = "settings"
T_LICENCES = "licences"
T_GITONIC = "gitonic"


# tracked tab

class TrackedView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._frameworksp = ttk.LabelFrame(
            self, text='Workspaces : ( use <NL> or <;> to separate )')
        self._frameworksp.grid(row=0, column=0, padx=5, sticky=tk.NSEW)

        self._workspaces = TNScrolledText(
            self._frameworksp, height=10, width=40)
        self._workspaces.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, )

        self._frameworkspbtn = ttk.Frame(self)
        self._frameworkspbtn.grid(row=0, column=1, padx=5, pady=5)

        self.refresh_btn = TNButton(
            self._frameworkspbtn, text="reload repositories from workspaces", image="refresh")
        self.refresh_btn.pack(pady=15)

        self.selall_btn = TNButton(
            self._frameworkspbtn, text="select all repositories", image="playlist_add")
        self.selall_btn.pack(pady=15)

        self.unselall_btn = TNButton(
            self._frameworkspbtn, text="unselect all repositories", image="playlist_remove")
        self.unselall_btn.pack(pady=15)

        self.frametracked = ttk.LabelFrame(
            self, text='Repositories found :')
        self.frametracked.grid(row=0, column=2, padx=5, sticky=tk.NSEW)

        self._tracked = TNListbox(self.frametracked,
                                  selectmode=tk.MULTIPLE, )
        self._tracked.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, )

        self._framerepopbtn = ttk.Frame(self)
        self._framerepopbtn.grid(row=0, column=3, padx=5, pady=5)

        self.pull_btn = TNButton(
            self._framerepopbtn, text="pull selected repositories", image="arrow_and_edge", hotkey="<Control-Key-p>")
        self.pull_btn.pack(padx=50, pady=15)

        self.fetch_btn = TNButton(
            self._framerepopbtn, text="fetch selected repositories", image="arrow_or_edge", hotkey="<Control-Key-P>")
        self.fetch_btn.pack(padx=50, pady=15)

        #

        self.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        #

    @property
    def workspaces(self):
        return self._workspaces.get_val()

    @workspaces.setter
    def workspaces(self, wsprop):
        self._workspaces.set_val(wsprop)

    @property
    def tracked(self):
        return self._tracked

    @tracked.setter
    def tracked(self, vals):
        return self._tracked.set_values(vals)


# changes tab
BRANCH = "branch"
FILE = "file"
STAGED = "staged"
UNSTAGED = "unstaged"
TYPE = "type"


class ChangesView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pane_changes = ttk.PanedWindow(
            self, orient=tk.HORIZONTAL, )
        self._pane_changes.pack(expand=True, fill=tk.BOTH)

        self._repos = TNListbox(self._pane_changes, selectmode=tk.SINGLE, )
        self._repos.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._pane_changes.add(self._repos)

        self.treechanges = TNTreeview(self, columns=(BRANCH, FILE,
                                                     UNSTAGED, STAGED, TYPE), show="headings")

        self.treechanges.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._pane_changes.add(self.treechanges)

        WIDTH = 75

        self.treechanges.config_column(
            BRANCH, text="Branch", width=int(WIDTH*1.5))
        self.treechanges.config_column(FILE, text="File", width=400, )
        self.treechanges.config_column(STAGED, text="Staged", width=WIDTH, )
        self.treechanges.config_column(
            UNSTAGED, text="Unstaged", width=WIDTH, )
        self.treechanges.config_column(
            TYPE, text="Type", width=int(WIDTH*1.5), )

        self._framechangesbtn = ttk.Frame(self)
        self._framechangesbtn.pack()

        self.refreshchanges_btn = TNButton(
            self._framechangesbtn, text="refresh changes from repositories", image="cycle", hotkey="<F1>")
        self.refreshchanges_btn.pack(side=tk.LEFT, padx=15, pady=7)

        self.selallchanges_btn = TNButton(
            self._framechangesbtn, text="select all changes", image="playlist_add", hotkey="<F2>")
        self.selallchanges_btn.pack(side=tk.LEFT, padx=15)

        self.unselallchanges_btn = TNButton(
            self._framechangesbtn, text="unselect all changes", image="playlist_remove", hotkey="<F3>")
        self.unselallchanges_btn.pack(side=tk.LEFT, padx=15)

        self.addchanges_btn = TNButton(
            self._framechangesbtn, text="add selected changes", image="shadow_add", hotkey="<Alt-Key-a>")
        self.addchanges_btn.pack(side=tk.LEFT, padx=15)

        self.undochanges_btn = TNButton(
            self._framechangesbtn, text="undo selected changes", image="shadow_minus", hotkey="<Alt-Key-q>")
        self.undochanges_btn.pack(side=tk.LEFT, padx=15)

        self.diffchanges_btn = TNButton(
            self._framechangesbtn, text="diff selected changes", image="compare_arrows", hotkey="<Alt-Key-w>")
        self.diffchanges_btn.pack(side=tk.LEFT, padx=15)

        self.autoformchanges_btn = TNButton(
            self._framechangesbtn, text="auto format selected changes", image="format_indent_increase", hotkey="<Alt-Key-f>")
        self.autoformchanges_btn.pack(side=tk.LEFT, padx=15)

        self.difftoolchanges_btn = TNButton(
            self._framechangesbtn, text="difftool selected changes", image="compare", hotkey="<Alt-Key-d>")
        self.difftoolchanges_btn.pack(side=tk.LEFT, padx=15)

    def clr_items(self):
        self.treechanges.clear()

    def add_item(self, iid, branch, file, staged, unstaged, type_info):
        widgetsid = self.treechanges.insert("", "end", text=iid)
        self.treechanges.set(widgetsid, BRANCH, branch)
        self.treechanges.set(widgetsid, FILE, file)
        self.treechanges.set(widgetsid, STAGED, staged)
        self.treechanges.set(widgetsid, UNSTAGED, unstaged)
        self.treechanges.set(widgetsid, TYPE, type_info)

    @property
    def repos(self):
        return self._repos


# commit tab

class CommitView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pane_msg = ttk.Frame(self)
        self._pane_msg.pack(side=tk.TOP, padx=15, pady=15, anchor=tk.NW)

        self._msg_lbl = ttk.Label(self._pane_msg, text="Message :")
        self._msg_lbl.grid(row=0, column=0, sticky=tk.E,)

        self.msg_cb = TNCombobox(self._pane_msg,)
        self.msg_cb.grid(row=0, column=1, sticky=tk.EW, padx=15, pady=15)

        self.msg_clr_btn = TNButton(
            self._pane_msg, text="Clear Commit Message", image="mop", hotkey="<Alt-Key-c>")
        self.msg_clr_btn.grid(row=0, column=2, sticky=tk.E)

        self.msg_text = TNScrolledText(self._pane_msg, width=60, height=8)
        self.msg_text.grid(row=1, column=0, columnspan=3)

        self._pane_msg.rowconfigure(0, weight=1)
        self._pane_msg.rowconfigure(1, weight=1)
        self._pane_msg.rowconfigure(2, weight=1)

        self._pane_msg.columnconfigure(0, weight=1)
        self._pane_msg.columnconfigure(1, weight=1)

        self._commit_extra = ttk.Frame(self)
        self._commit_extra.pack(side=tk.BOTTOM, anchor=tk.NE)

        self.commit_btn = TNButton(
            self._commit_extra, text="commit to tracked repositories", image="contract_edit", hotkey="<Alt-Key-x>")
        self.commit_btn.pack(side=tk.LEFT, padx=15, pady=7)

        self.push_btn = TNButton(
            self._commit_extra, text="push tracked repositories", image="cloud_upload", hotkey="<Alt-Key-s>")
        self.push_btn.pack(side=tk.LEFT, padx=15)

        self.magic_btn = TNButton(
            self._commit_extra, text="commit and push tracked repositories", image="wand_stars", hotkey="<Alt-Key-e>")
        self.magic_btn.pack(side=tk.LEFT, padx=15)

        self.pushtags_ck = TNCheckButton(self._commit_extra, text="Push Tags",
                                         infotext="select to push tracked repositories tags when pushing next time",
                                         image="new_label", compound=tk.LEFT)
        self.pushtags_ck.pack(side=tk.LEFT, padx=15)

        self.clrcommit_ck = TNCheckButton(
            self._commit_extra, text="Clear Message after Commit")
        self.clrcommit_ck.pack(side=tk.LEFT, padx=15)


# log tab


class LogView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pane_log = ttk.PanedWindow(self, orient=tk.HORIZONTAL, )
        self._pane_log.pack(expand=True, fill=tk.BOTH)

        self.repos = TNListbox(
            self._pane_log, selectmode=tk.SINGLE, )
        self.repos.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._pane_log.add(self.repos)

        self.log_detail_bucket = ttk.Frame(self._pane_log)
        self.log_detail_bucket.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._pane_log.add(self.log_detail_bucket)

        # add default "all" logs to bucket
        self.log_detail = TNScrolledText(self.log_detail_bucket)
        self.log_detail.set_readonly()
        self.log_detail.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        #

        self._tmplog = ttk.Frame(self)
        self._tmplog.pack(side=tk.BOTTOM, anchor=tk.SW, pady=7)

        self.clear_btn = TNButton(self._tmplog, image="mop")
        self.clear_btn.pack(side=tk.LEFT,)

        self.follow_ck = TNCheckButton(self._tmplog, text="follow log")
        self.follow_ck.pack(side=tk.LEFT, padx=7)

        self.other_logs = {}
        self.cur_log = self.log_detail

    def get_other_log(self, nam):
        if nam in self.other_logs:
            return self.other_logs[nam]

        otherlog_detail = TNScrolledText(self.log_detail_bucket)
        otherlog_detail.set_readonly()
        self.other_logs[nam] = otherlog_detail
        return otherlog_detail

    def set_log_visible(self, thelog):
        self.cur_log.pack_forget()
        self.cur_log = thelog
        self.cur_log.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def get_other_names(self):
        return self.other_logs.keys()

    def rm_other_log(self, nam):
        thelog = self.get_other_log(nam)
        if thelog == self.cur_log:
            self.show_all_log()
        thelog.destroy()
        del self.other_logs[nam]

    def clr_other_logs(self):
        for nam, thelog in self.other_logs.items():
            thelog.clr()

    def show_all_log(self):
        self.set_log_visible(self.log_detail)
        # self.log_detail.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def hide_all_log(self):
        self.log_detail.pack_forget()


# log expert tab

class ExtraLogView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logdetail = TNScrolledText(self)
        self.logdetail.set_readonly()
        self.logdetail.pack(side=tk.TOP, expand=True,
                            fill=tk.BOTH, anchor=tk.NW)

        self._tmpxlog = ttk.Frame(self)
        self._tmpxlog.pack(side=tk.BOTTOM, anchor=tk.SW, pady=7)

        self.clear_btn = TNButton(self._tmpxlog, image="mop")
        self.clear_btn.pack(side=tk.LEFT,)

        self.follow_ck = TNCheckButton(self._tmpxlog, text="follow log")
        self.follow_ck.pack(side=tk.LEFT, padx=7)

    def append(self, s):
        self.logdetail.append(s)


# preferences tab


class PreferencesView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._lbl_min_text_len = ttk.Label(
            self, text="minimum commit text length :")
        self._lbl_min_text_len.grid(row=0, column=0, pady=15, sticky=tk.W)
        self.inp_min_text_len = TNEntryInt(self)
        self.inp_min_text_len.grid(row=0, column=1, pady=7, sticky=tk.W)

        self._lbl_max_records_log_len = ttk.Label(
            self, text="maximal records in log history :")
        self._lbl_max_records_log_len.grid(
            row=1, column=0, pady=7, sticky=tk.W)

        self.inp_max_records_log_len = TNEntryInt(self)
        self.inp_max_records_log_len.grid(row=1, column=1, pady=7, sticky=tk.W)

        self._lbl_max_records_commit_len = ttk.Label(
            self, text="maximal records in commit history :")
        self._lbl_max_records_commit_len.grid(
            row=2, column=0, pady=7, sticky=tk.W)

        self.inp_max_records_commit_len = TNEntryInt(self)
        self.inp_max_records_commit_len.grid(
            row=2, column=1, pady=7, sticky=tk.W)

        self._lbl_git_exe = ttk.Label(self, text="git executable :")
        self._lbl_git_exe.grid(row=3, column=0, pady=7, sticky=tk.W)

        self.inp_git_exe = TNEntryString(self)
        self.inp_git_exe.grid(row=3, column=1, pady=7, sticky=tk.W)

        self._lbl_show__changes_tab = ttk.Label(
            self, text="always show changes tab on startup (*):")
        self._lbl_show__changes_tab.grid(row=4, column=0, pady=7, sticky=tk.W)

        self.inp_show__changes_tab = TNCheckButton(self)
        self.inp_show__changes_tab.grid(row=4, column=1, pady=7, sticky=tk.W)

        self._lbl_expert_mode = ttk.Label(
            self, text="expert mode. shows more debug log :")
        self._lbl_expert_mode.grid(row=5, column=0, pady=7, sticky=tk.W)

        self.inp_lbl_expert_mode = TNCheckButton(self)
        self.inp_lbl_expert_mode.grid(row=5, column=1, pady=7, sticky=tk.W)

        self._lbl_max_records_expert_log_len = ttk.Label(
            self, text="maximal records in expert log history :")
        self._lbl_max_records_expert_log_len.grid(
            row=7, column=0, pady=7, sticky=tk.W)

        self.inp_max_records_expert_log_len = TNEntryInt(self)
        self.inp_max_records_expert_log_len.grid(
            row=7, column=1, pady=7, sticky=tk.W)

        self._lbl_open_config_folder = ttk.Label(
            self, text="open gitonic config files folder :")
        self._lbl_open_config_folder.grid(row=8, column=0, pady=7, sticky=tk.W)

        self.inp_open_config_folder = TNButton(self, image="folder_open",)
        self.inp_open_config_folder.grid(row=8, column=1, pady=7, sticky=tk.W)

        self._lbl_max_threads = ttk.Label(
            self, text="maximal threads :")
        self._lbl_max_threads.grid(
            row=9, column=0, pady=7, sticky=tk.W)

        self.inp_max_threads = TNEntryInt(self)

        # 0 -> switch off balancer
        self.inp_max_threads.min_val = 0
        # self.inp_max_threads.max_val = 100

        self.inp_max_threads.grid(
            row=9, column=1, pady=7, sticky=tk.W)

        self._lbl_hint = ttk.Label(
            self, text="(*) : requires restart of gitonic")
        self._lbl_hint.grid(row=10, column=0, pady=7, sticky=tk.W)

#
# licence
#


class LicenseInfo(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._name_lbl = TNLabel(self)
        self._name_lbl.pack(anchor=tk.W, pady=7, padx=7)

        self._homepage_lbl = TNLabelClickUrl(self)
        self._homepage_lbl.pack(anchor=tk.W, pady=7, padx=7)

        self._text = TNScrolledText(self)
        self._text.readonly = True
        self._text.pack(anchor=tk.W, pady=7, padx=7)

    def setup(self, name, homepage, filenam):
        self._name_lbl.set_val(name)
        self._homepage_lbl.set_val(homepage)
        try:

            basepath = os.path.dirname(__file__)
            fnam = os.path.join(basepath, filenam)

            with open(fnam) as f:
                self._text.set_val(f.read())
        except Exception as ex:
            print("license", ex, file=sys.stderr)

        return self


class LicenseView(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._license_nb = TNNotebook(self)
        self._license_nb.pack(pady=15)

        gitonictab = LicenseInfo(self.ref(),).setup(
            T_GITONIC, "https://www.github.com/kr-g/gitonic", "./otherdeps/LICENSE-gitonic")
        gitonictab.pack(expand=True, fill=tk.BOTH)
        self.add(gitonictab, text=T_GITONIC, )

        tktooltiptab = LicenseInfo(self.ref(),).setup(
            "tkinter-tooltip", "https://github.com/gnikit/tkinter-tooltip",
            "./otherdeps/LICENSE-tktootip")
        tktooltiptab.pack(expand=True, fill=tk.BOTH)
        self.add(tktooltiptab, text="tkinter tooltip", )

        googletab = LicenseInfo(self.ref(),).setup("material-design-icons",
                                                   "https://github.com/google/material-design-icons",
                                                   "./material_fonts/LICENSE")
        googletab.pack(expand=True, fill=tk.BOTH)
        self.add(googletab, text="google icons", )

    def ref(self):
        return self._license_nb

    def add(self, w, text):
        self._license_nb.add(w, text=text, )
