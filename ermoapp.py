import curses
from datetime import timedelta

from utils import functions

waiting = timedelta(seconds=0.5)


curses.initscr()


curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

MAIN_COLOR = curses.color_pair(1)
MAIN_COLOR_R = curses.color_pair(2)
TITLE_COLOR = curses.color_pair(3)
SECONDARY_COLOR = curses.color_pair(4)


def main(stdscr):
    stdscr.clear()
    stdscr.bkgd(' ', curses.COLOR_BLACK)
    mm_idx = 0
    ermo_fun = functions.ermo_fun(stdscr, TITLE_COLOR, MAIN_COLOR,
                                  MAIN_COLOR_R, SECONDARY_COLOR)

# NOTA==============================
# LIMPIAR DE STDSCR.CLEAR Y DEJARLOS EN LA CLASE SOLO
# QUE CREO QUE HAY DE MÄS
# ===================================

    while True:
        ermo_fun.print_menu(mm_idx)
        mm_key = stdscr.getch()

        if (mm_key == curses.KEY_UP and
                mm_idx > 0):
            mm_idx -= 1
        elif (mm_key == curses.KEY_DOWN and
                mm_idx < len(ermo_fun.menu)):
            mm_idx += 1

        if mm_key == ord('q'):
            break
        elif (mm_key == curses.KEY_RIGHT and
              mm_idx == 0):

            ermo_fun.ermo_help()

        elif (mm_key == curses.KEY_RIGHT and
              mm_idx == 1):
            ermo_fun.ermo_clock()

        elif (mm_key == curses.KEY_RIGHT and
              mm_idx == 2):

            ermo_fun.sms_keyboard(waiting)


curses.wrapper(main)
