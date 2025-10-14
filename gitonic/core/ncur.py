#!/usr/bin/env python3

import curses


def main(stdscr):
    while True:

        key = stdscr.getch()

        if key == ord('q'):
            break  # quit app

        elif key == curses.KEY_UP:
            stdscr.addstr(0, 0, "UP  ")  # print feedback

        elif key == curses.KEY_DOWN:
            stdscr.addstr(1, 0, "DOWN")

        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
