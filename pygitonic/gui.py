import os

from tile import *

import tkinter
from tkinter import Tk

from file import FileStat
from gitutil import GitWorkspace

#

tk_root = Tk()

mainframe = Tile(tk_root=tk_root, idn="mainframe")


def toogleLabel():
    print("toogleLabel")
    lbl = gt("the_label")
    lbl._visible = not lbl._visible
    mainframe.layout()


main = TileRows(
    source=[
        TileLabel(caption="test label", idn="the_label"),
        TileEntryInt(
            caption="input",
            value=1234,
        ),
        TileLabelButton(
            caption="change the label", commandtext="toogle", on_click=toogleLabel
        ),
    ]
)


all_tabs = TileTab(
    source=[
        (
            "settings",
            TileRows(
                source=[
                    TileEntryButton(
                        caption="workspace", commandtext="select", idn="workspace"
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
                    TileLabelButton(
                        caption="selected", commandtext="pull", idn="pull_workspace"
                    ),
                ]
            ),
        ),
        (
            "changes",
            TileRows(
                source=[
                    TileLabel(caption=""),
                    TileEntryListbox(caption="", idn="changes"),
                    TileLabelButton(
                        caption="",
                        commandtext="refresh",
                        idn="refresh_add_workspace",
                    ),
                    TileCols(
                        source=[
                            TileLabelButton(
                                caption="",
                                commandtext="add",
                                idn="add_workspace",
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
                    TileLabel(caption="commit"),
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
                    TileEntryButton(
                        caption="new tag name",
                        commandtext="tag",
                        idn="tag_workspace",
                    ),
                ]
            ),
        ),
        (
            "about",
            TileRows(source=[]),
        ),
    ]
)

main_content = TileRows(source=[main, all_tabs])

mainframe.resize_grip()

# mainframe.add(main)
mainframe.add(main_content)
mainframe.layout()


frepo = FileStat("~/repo")
gt("workspace").set_val(frepo.name)

gws = GitWorkspace(frepo.name)
gws.refresh()
gws.refresh_status()

gt("gits").set_values(gws.gits.keys())


print(tk_root.geometry())
print(tk_root.winfo_reqwidth(), tk_root.winfo_reqheight())

mainframe.mainloop()
