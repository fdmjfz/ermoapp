import time
from datetime import datetime
import curses

from utils import drawings


TITLE = drawings.TITLE
TITLE_HEIGHT = drawings.TITLE_HEIGHT
TITLE_WIDTH = drawings.TITLE_WIDTH


class ermo_fun:
    def __init__(self, stdscr, title_color,
                 main_color, main_color_r, secondary_color):
        self.menu = [
            'Ayuda', 'Reloj', 'Agenda'
        ]

        self.num_pad = [
            "abc", "def", "ghi",
            "jkl", "mno", "pqrs",
            "tuv", "wxyz"
        ]

        self.stdscr = stdscr
        self.title_color = title_color
        self.main_color = main_color
        self.main_color_r = main_color_r
        self.secondary_color = secondary_color
        self.h, self.w = stdscr.getmaxyx()

    def print_menu(self, mm_idx):
        self.stdscr.clear()
        self.stdscr.box()

        for idx, row in enumerate(self.menu):
            x = 5
            y = self.h//2 - len(self.menu)//2 + idx

            if idx == mm_idx:
                self.stdscr.addstr(y, x, row,
                                   self.main_color_r)
            else:
                self.stdscr.addstr(y, x, row,
                                   self.main_color)

            arrow_x = x + len(row) + 1
            self.stdscr.addstr(y, arrow_x, "->",
                               self.main_color)

    def ermo_help(self):
        self.stdscr.clear()

        self.stdscr.nodelay(True)
        title_win_y = 0
        title_win_x = self.w//2 - TITLE_WIDTH//2

        title_win = self.stdscr.subwin(TITLE_HEIGHT, TITLE_WIDTH,
                                       title_win_y, title_win_x)
        title_win.addstr(0, 0, TITLE)
        while True:
            key = self.stdscr.getch()

            self.stdscr.addstr(0, 0, "AYUDA")

            self.stdscr.refresh()

            if key == curses.KEY_LEFT:
                break

        self.stdscr.nodelay(False)

    def ermo_clock(self):
        self.stdscr.clear()
        self.stdscr.nodelay(True)
        while True:
            key = self.stdscr.getch()

            clock = datetime.now()
            clock = clock.strftime('%Y-%m-%d %H:%M:%S')
            self.stdscr.addstr(0, 0, clock)

            self.stdscr.refresh()

            if key == curses.KEY_LEFT:
                break

        self.stdscr.nodelay(False)

    def sms_keyboard(self, waiting):
        self.stdscr.clear()
        idx = None
        message = str()
        while True:
            key = self.stdscr.getkey()
            if key == 'KEY_BACKSPACE':
                message = message[:-1]
            elif key == 'KEY_LEFT':
                break

            else:
                time.sleep(0.1)
                start_time = datetime.now()
                self.stdscr.nodelay(True)
                subidx = 0

                while datetime.now() - start_time <= waiting:
                    try:
                        new_key = self.stdscr.getkey()
                    except curses.error:
                        new_key = 0

                    try:
                        idx = int(key) - 2
                    except ValueError:
                        continue

                    if new_key == key:
                        subidx += 1
                        start_time = datetime.now()

                    if subidx >= len(self.num_pad[idx]):
                        subidx -= len(self.num_pad[idx])

                if isinstance(idx, int):
                    if (idx >= 0 and idx <= 7):
                        message = message + self.num_pad[idx][subidx]
                    elif idx == -1:
                        message = message + ' '

            subidx = 0
            self.stdscr.nodelay(False)
            self.stdscr.clear()
            self.stdscr.refresh()
            self.stdscr.addstr(0, 0, "idx: ")
            self.stdscr.addstr(0, 8, str(idx))
            self.stdscr.addstr(1, 0, "subidx: ")
            self.stdscr.addstr(1, 8, str(subidx))
            self.stdscr.addstr(2, 0, "messag: ")
            self.stdscr.addstr(2, 8, message)

        return message
