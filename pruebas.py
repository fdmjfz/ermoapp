import curses

curses.initscr()


def main(stdscr):
    y, x = stdscr.getmaxyx()

    stdscr.addstr(5, 5, str(y))
    stdscr.addstr(6, 5, str(x))
    stdscr.getch()


curses.wrapper(main)
