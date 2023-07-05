import sys
import time
import tkinter
from tkinter import Tk

from .gui import TkCmd, Tile, TileRows, TileCols, TileLabelButton
from .gui import startup_gui, get_main, fconfigdir
from .gui import gt

from .icons import get_icon

from .file import FileStat
from .singleinstance import (
    check_instance,
    check_and_bring_to_front,
    create_client_socket,
)

from gitonic import set_tk_root, get_tk_root


# main


debug = False

_last_esc_hit = None
_cancel_task = None


def double_esc_check_and_quit_all(frame):
    print("double esc check installed")

    def _check():
        print("got esc")

        global _last_esc_hit, _cancel_task

        now = time.time_ns()
        if _last_esc_hit:
            delta = now - _last_esc_hit
            delta /= 1000 * 1000
            delta = int(delta)
            print("delta", delta)
            if delta < 450:
                print("good bye.")
                frame.quit()
                sys.exit()

        _last_esc_hit = now
        _cancel_task = get_tk_root().after(500, minimize)
        print("wait for next esc, or minimize")

    return _check


def quit_all(frame):
    def quit_():
        print("quit_all")
        # removes all, including threads
        # sys.exit()
        # soft, state remains
        # download_stop()
        frame.quit()
        if not debug:
            sys.exit()

    return quit_


def minimize():
    print("minimize")
    get_tk_root().iconify()


def _move_tab_focus(direction=1):
    mt = gt("maintabs")
    l = len(mt.keys())
    pos = mt.get_index()
    pos += direction
    pos %= l
    mt.set_index(pos)
    mt.focus_first_active_tab()


def f5_handler(ev):
    print("f5", ev)
    _move_tab_focus(-1)


def f6_handler(ev):
    print("f5", ev)
    _move_tab_focus()


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
    rc = check_and_bring_to_front(sock, get_tk_root())
    if rc is not None:
        print("bring to front client request")


tkcmd = None

# end-of single instance


def main_func(debug_=False):
    global debug
    debug = debug_

    global tk_root
    tk_root = set_tk_root(Tk())

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
                        commandtext="good bye - click button or 2x ESC (quickly)",
                        icon=get_icon("right-from-bracket"),
                        command=quit_all(mainframe),
                    ),
                    TileLabelButton(
                        caption="minimize",
                        commandtext="minimize me",
                        icon=get_icon("minimize"),
                        hotkey="<Escape>",
                        command=double_esc_check_and_quit_all(mainframe),
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

    tk_root.bind("<F5>", f5_handler)
    tk_root.bind("<F6>", f6_handler)

    startup_gui()

    mainframe.mainloop()
