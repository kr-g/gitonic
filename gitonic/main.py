import tkinter
from tkinter import Tk

from gitonic.gui import TkCmd, Tile, TileRows, TileCols, TileLabelButton
from gitonic.gui import startup_gui, main

# main

tk_root = Tk()


def quit_all(frame):
    def quit_():
        print("quit_all")
        # removes all, including threads
        # sys.exit()
        # soft, state remains
        # download_stop()
        frame.quit()

    return quit_


def minimize():
    print("minimize")
    tk_root.iconify()


# sample


def _r(self):
    print(self.opts.i, self._info)
    self.opts.i -= 1
    if self.opts.i < 0:
        return 0


tkcmd = TkCmd().start(tk_root, _r, i=5)

# end-of sample


def main_func():

    mainframe = Tile(tk_root=tk_root, idn="mainframe")

    main_content = TileRows(
        source=[
            TileCols(
                source=[
                    TileLabelButton(
                        caption="close app",
                        commandtext="bye",
                        command=quit_all(mainframe),
                    ),
                    TileLabelButton(
                        caption="", commandtext="minimize", command=minimize
                    ),
                ]
            ),
            main,
        ]
    )

    mainframe.tk.protocol("WM_DELETE_WINDOW", quit_all(mainframe))
    mainframe.tk.bind("<Escape>", lambda e: minimize())

    mainframe.title("gitonic")
    mainframe.resize_grip()

    mainframe.add(main_content)
    mainframe.layout()

    startup_gui()
    mainframe.mainloop()
