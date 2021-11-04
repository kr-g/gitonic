VERSION = "v0.0.1-a"

import os

from tile import *

import tkinter
from tkinter import Tk

from file import FileStat
from gitutil import GitWorkspace

#

frepo = FileStat("~/repo")

tk_root = Tk()

mainframe = Tile(tk_root=tk_root, idn="mainframe")


main = TileTab(
    source=[
        (
            "settings",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileDirectorySelect(
                        caption="select workspace",
                        commandtext="...",
                        idn="workspace",
                        path=frepo.name,
                    ),
                ]
            ),
        ),
        (
            "track git's",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntryListbox(
                        caption="",
                        idn="gits",
                        max_show=15,
                        width=40,
                        select_many=True,
                        map_value=lambda x: os.path.basename(x),
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="workspace",
                                commandtext="refresh",
                            ),
                            TileLabelButton(
                                caption="all",
                                commandtext="select",
                                command=lambda: gt("gits").set_selection(-1),
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="un-select",
                                command=lambda: gt("gits").clr_selection(),
                            ),
                        ]
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="pull",
                                commandtext="selected",
                                idn="pull_selected_workspace",
                            ),
                            TileLabelButton(
                                caption="", commandtext="all", idn="pull_all_workspace"
                            ),
                        ]
                    ),
                ]
            ),
        ),
        (
            "changes",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileTreeView(
                        caption="",
                        idn="changes",
                        header=[
                            ("git", None),
                            ("file", None),
                            ("state", None),
                            ("type", None),
                        ],
                    ),
                    TileLabelButton(
                        caption="",
                        commandtext="refresh",
                        idn="refresh_add_workspace",
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="selected",
                                commandtext="add",
                                idn="add_workspace",
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="unstage",
                                idn="unstage_workspace",
                            ),
                            TileLabelButton(
                                caption="all",
                                commandtext="select",
                                idn="sel_all_workspace",
                            ),
                            TileLabelButton(
                                caption="",
                                commandtext="unselect",
                                idn="unsel_all_workspace",
                                command=lambda: gt("changes").clr_selection(),
                            ),
                        ]
                    ),
                ]
            ),
        ),
        (
            "commit",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntry(caption="", idn="commit_short", width=40),
                    TileEntryText(caption="", idn="commit_long", height=10),
                    TileLabelButton(
                        caption="",
                        commandtext="commit",
                        idn="commit_workspace",
                    ),
                ]
            ),
        ),
        (
            "tag",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntryButton(
                        caption="new tag name",
                        commandtext="tag",
                        idn="tag_workspace",
                    ),
                ]
            ),
        ),
        (
            "log",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntryText(caption="", idn="log", height=20),
                    TileLabelButton(
                        caption="",
                        commandtext="clear",
                        idn="clr_log",
                    ),
                ]
            ),
        ),
    ]
)


def quit_all(frame):
    def quit():
        print("quit_all")
        # removes all, including threads
        # sys.exit()
        # soft, state remains
        # download_stop()
        frame.quit()

    return quit


def minimize():
    print("minimize")
    tk_root.iconify()


url_homepage = "https://github.com/kr-g/pygitonic"


def open_homepage():
    import webbrowser

    webbrowser.get().open(url_homepage, new=0)


main_content = TileRows(
    source=[
        TileCols(
            source=[
                TileLabelButton(
                    caption="close app", commandtext="bye", command=quit_all(mainframe)
                ),
                TileLabelButton(caption="", commandtext="minimize", command=minimize),
            ]
        ),
        main,
        TileCols(
            source=[
                TileLabelClick(
                    caption=f"gitonic - {url_homepage}",
                    on_click=open_homepage,
                ),
                TileLabel(
                    caption=f"version: {VERSION}",
                ),
            ]
        ),
    ]
)

mainframe.tk.protocol("WM_DELETE_WINDOW", quit_all(mainframe))
mainframe.tk.bind("<Escape>", lambda e: minimize())

mainframe.title("gitonic")
mainframe.resize_grip()

mainframe.add(main_content)
mainframe.layout()

# init


gws = GitWorkspace(frepo.name)
gws.refresh()
gws.refresh_status()

gt("gits").set_values(sorted(gws.gits.keys()))

changes = []
for path, git in gws.gits.items():
    rnam = FileStat(path).basename()
    if len(git.status) > 0:
        for stat in git.status:
            fs = git.stat(stat)
            #
            gst = {
                "git": rnam,
                "file": stat.file,
                "state": stat.mode,
                "type": ("file" if fs.is_file() else "dir"),
            }
            changes.append(gst)

gt("changes").set_values(changes)

# end-of init

print(tk_root.geometry())
print(tk_root.winfo_reqwidth(), tk_root.winfo_reqheight())

mainframe.mainloop()
