from tile import *

import tkinter
from tkinter import Tk

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

mainframe.resize_grip()

mainframe.add(main)
mainframe.layout()

print(tk_root.geometry())
print(tk_root.winfo_reqwidth(), tk_root.winfo_reqheight())

mainframe.mainloop()
