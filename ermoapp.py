import curses
from datetime import timedelta
import time

from utils import functions

waiting = timedelta(seconds=0.5)


curses.initscr()
curses.curs_set(False)

curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)

MAIN_COLOR = curses.color_pair(1)
MAIN_COLOR_R = curses.color_pair(2)
TITLE_COLOR = curses.color_pair(3)
SECONDARY_COLOR = curses.color_pair(4)
SECONDARY_COLOR_R = curses.color_pair(5)


def main(stdscr):
    mm_idx = 0
    ermo_fun = functions.ermo_fun(stdscr, TITLE_COLOR, MAIN_COLOR,
                                  MAIN_COLOR_R, SECONDARY_COLOR,
                                  SECONDARY_COLOR_R)

    while True:
        ermo_fun.print_menu(mm_idx, True)
        mm_key = stdscr.getch()

        if (mm_key == curses.KEY_LEFT and
                mm_idx > 0):
            mm_idx -= 1
        elif (mm_key == curses.KEY_RIGHT and
                mm_idx < len(ermo_fun.menu) - 1):
            mm_idx += 1

        if mm_key == ord('q'):
            break
        elif (mm_key == curses.KEY_UP and
              mm_idx == 0):
            ermo_fun.ermo_help(mm_idx)
        elif (mm_key == curses.KEY_UP and
              mm_idx == 1):
            ermo_fun.ermo_agenda(mm_idx)


curses.wrapper(main)
