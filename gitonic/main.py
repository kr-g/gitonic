import tkinter
from tkinter import Tk

from .gui import TkCmd, Tile, TileRows, TileCols, TileLabelButton
from .gui import startup_gui, get_main, fconfigdir

from .icons import get_icon

from .file import FileStat
from .singleinstance import (
    check_instance,
    check_and_bring_to_front,
    create_client_socket,
)

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


# single instance handling

pnam = FileStat(fconfigdir.name).join(["socket"])
sock = None


def try_switch_app():
    global sock
    # set up server if possible
    sock, port = check_instance(pnam.name)
    if sock is None:
        # open connection to server, and quit
        sock = create_client_socket(port)
        return sock


def do_serv_socket(self):
    rc = check_and_bring_to_front(sock, tk_root)
    if rc is not None:
        print("bring to front client request")


tkcmd = None

# end-of single instance


def main_func():

    if try_switch_app():
        print("switched to server instance")
        return

    global tkcmd
    tkcmd = TkCmd().start(tk_root, command=do_serv_socket)

    mainframe = Tile(tk_root=tk_root, idn="mainframe")

    main = get_main()

    main_content = TileRows(
        source=[
            TileCols(
                source=[
                    TileLabelButton(
                        caption="close app",
                        commandtext="good bye",
                        icon=get_icon("right-from-bracket"),
                        hotkey="<Control-x>",
                        command=quit_all(mainframe),
                    ),
                    TileLabelButton(
                        caption="minimize",
                        commandtext="minimize me",
                        icon=get_icon("minimize"),
                        hotkey="<Escape>",
                        command=minimize,
                    ),
                ]
            ),
            main,
        ]
    )

    mainframe.tk.protocol("WM_DELETE_WINDOW", quit_all(mainframe))

    mainframe.title("gitonic")
    mainframe.resize_grip()

    mainframe.add(main_content)
    mainframe.layout()

    startup_gui()

    mainframe.mainloop()
