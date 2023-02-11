import curses

from utils import functions


curses.initscr()
curses.curs_set(False)

curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)

MAIN_COLOR = curses.color_pair(1)
MAIN_COLOR_R = curses.color_pair(2)
TITLE_COLOR = curses.color_pair(3)
SECONDARY_COLOR = curses.color_pair(4)
SECONDARY_COLOR_R = curses.color_pair(5)


def main(stdscr):
    mm_idx = 0
    ermo = functions.ermo_fun(stdscr, TITLE_COLOR, MAIN_COLOR,
                              MAIN_COLOR_R, SECONDARY_COLOR,
                              SECONDARY_COLOR_R)

    while True:
        # Inicializacion menu
        ermo.stdscr.box()
        ermo.display_navigation(ermo.menu, mm_idx, True,
                                1)

        mm_key = ermo.stdscr.getch()
        mm_idx = ermo.update_index(menu_list=ermo.menu, key=mm_key,
                                   index=mm_idx, horizontal=True)
        ermo.display_navigation(menu_list=ermo.menu, index=mm_idx,
                                horizontal=True, level=1)

        if mm_key == curses.KEY_UP and mm_idx == 1:
            ermo.ermo_agenda()
        elif mm_key == curses.KEY_UP and mm_idx == 2:
            ermo.ermo_hc12(0.5)
        elif mm_key == ord('q'):
            break


curses.wrapper(main)
