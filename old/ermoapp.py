import curses
from datetime import datetime, timedelta
import time


waiting = timedelta(seconds=0.5)

num_pad = [
    "abc", "def", "ghi",
    "jkl", "mno", "pqrs",
    "tuv", "wxyz"
]


curses.initscr()


def main(stdscr):
    idx = None
    message = str()
    while True:
        key = stdscr.getkey()
        time.sleep(0.1)
        start_time = datetime.now()
        stdscr.nodelay(True)
        subidx = 0

        while datetime.now() - start_time <= waiting:
            try:
                new_key = stdscr.getkey()
            except curses.error:
                new_key = 0

            try:
                idx = int(key) - 2
            except ValueError:
                continue

            if new_key == key:
                subidx += 1
                start_time = datetime.now()

            if subidx >= len(num_pad[idx]):
                subidx -= len(num_pad[idx])

        if isinstance(idx, int):
            if (idx >= 0 and idx <= 7):
                message = message + num_pad[idx][subidx]
            elif idx == -1:
                message = message + ' '

        subidx = 0
        stdscr.nodelay(False)
        stdscr.refresh()
        stdscr.addstr(0, 0, "idx: ")
        stdscr.addstr(0, 8, str(idx))
        stdscr.addstr(1, 0, "subidx: ")
        stdscr.addstr(1, 8, str(subidx))
        stdscr.addstr(2, 0, "messag: ")
        stdscr.addstr(2, 8, message)


curses.wrapper(main)
