import curses
import npyscreen
import time

curses.initscr()
curses.curs_set(False)


texto = """
Benvido á APP do Ermo!

Dende o noso refuxio dámoslle parabéns por obter un dispositivo PipBoy.
Lembre de andarse con ollo e de agardar por instruccións.

Sorte no Ermo!
"""


def main(stdscr):
    stdscr.clear()
    for i in range(0, len(texto)):
        string = texto[:i]
        stdscr.addstr(0, 0, string)
        stdscr.refresh()

        time.sleep(0.05)

    stdscr.getch()


curses.wrapper(main)
