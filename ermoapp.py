import curses
from datetime import timedelta

from utils import functions


waiting = timedelta(seconds=0.5)
menu = [
    'Clock', 'Agenda'
]


curses.initscr()

curses.start_color()

curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

MAIN_COLOR = curses.color_pair(1)
MAIN_COLOR_R = curses.color_pair(2)


def print_menu(stdscr, menu_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    for idx, row in enumerate(menu):
        x = 0
        y = h//2 - len(menu)//2 + idx

        if idx == menu_idx:
            stdscr.addstr(y, x, row, MAIN_COLOR_R)
        else:
            stdscr.addstr(y, x, row, MAIN_COLOR)


def main(stdscr):
    mm_idx = 0

    print_menu(stdscr, mm_idx)

    while True:
        mm_key = stdscr.getch()
        stdscr.clear()

        if mm_key == ord('q'):
            break

        if (mm_key == curses.KEY_UP and
                mm_idx > 0):
            mm_idx -= 1
        elif (mm_key == curses.KEY_DOWN and
                mm_idx < len(menu)):
            mm_idx += 1

        print_menu(stdscr, mm_idx)


curses.wrapper(main)
