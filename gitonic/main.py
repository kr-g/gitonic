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
