from tile import *

import tkinter
from tkinter import Tk

tk_root = Tk()

mainframe = Tile(tk_root=tk_root, idn="mainframe")


def toogleLabel():
    print("toogleLabel")
    lbl = gt("the_label")
    print(lbl)
    lbl._visible = not lbl._visible
    mainframe.layout()


main = TileRows(
    source=[
        TileLabel(caption="test label", idn="the_label"),
        TileLabelButton(
            caption="change the label", commandtext="toogle", on_click=toogleLabel
        ),
    ]
)

mainframe.add(main)
mainframe.layout()

mainframe.mainloop()
