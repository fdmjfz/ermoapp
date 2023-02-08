import time
from datetime import datetime
import pandas as pd
import curses
import os

from utils import drawings


TITLE = drawings.TITLE
TITLE_HEIGHT = drawings.TITLE_HEIGHT
TITLE_WIDTH = drawings.TITLE_WIDTH


class ermo_fun:
    def __init__(self, stdscr, title_color,
                 main_color, main_color_r, secondary_color,
                 secondary_color_r):
        self.menu = [
            'Ayuda', 'Agenda',
        ]
        self.num_pad = [
            "abc", "def", "ghi",
            "jkl", "mno", "pqrs",
            "tuv", "wxyz"
        ]
        self.agenda_submenu = [
            "Cargar", "Gestionar"
        ]

        self.stdscr = stdscr
        self.title_color = title_color
        self.main_color = main_color
        self.main_color_r = main_color_r
        self.secondary_color = secondary_color
        self.secondary_color_r = secondary_color_r
        self.h, self.w = stdscr.getmaxyx()

    def print_submenu(self, submenu_list, sm_idx):
        sm_item_sep = self.w//(len(submenu_list) + 2)
        x = sm_item_sep

        for idx, row in enumerate(submenu_list):
            y = self.h - 2

            if idx == sm_idx:
                self.stdscr.addstr(y, x, row,
                                   self.secondary_color_r)
            else:
                self.stdscr.addstr(y, x, row,
                                   self.secondary_color)
            x += sm_item_sep

    def print_menu(self, mm_idx, mm=True):
        self.stdscr.bkgd(' ', self.main_color)
        self.stdscr.clear()
        self.stdscr.box()

        if mm:
            title_win_y = 1
            title_win_x = self.w//2 - TITLE_WIDTH//2
            title_win = self.stdscr.subwin(TITLE_HEIGHT, TITLE_WIDTH,
                                           title_win_y, title_win_x)
            title_win.addstr(0, 0, TITLE,
                             self.title_color)
            mm_text = "< Esq. ^ Entrar  v Saír  Der. >"
            x_mm_text = self.w//2 - len(mm_text)//2
            y_mm_text = self.h//2
            self.stdscr.addstr(y_mm_text, x_mm_text, mm_text,
                               self.secondary_color)

        mm_item_sep = self.w//(len(self.menu) + 2)
        x = mm_item_sep

        for idx, row in enumerate(self.menu):
            y = self.h - 1

            if idx == mm_idx:
                self.stdscr.addstr(y, x, row,
                                   self.main_color_r)
            else:
                self.stdscr.addstr(y, x, row,
                                   self.main_color)
            x += mm_item_sep

    def ermo_help(self, mm_idx):
        self.print_menu(mm_idx, False)

        while True:
            key = self.stdscr.getch()

            self.stdscr.refresh()

            if key == curses.KEY_DOWN:
                break

    def sms_keyboard(self, mm_idx, waiting):
        self.print_menu(mm_idx, False)
        idx = None
        message = str()
        while True:
            key = self.stdscr.getkey()
            if key == 'KEY_BACKSPACE':
                message = message[:-1]
            elif key == 'KEY_DOWN':
                break

            else:
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

                    time.sleep(0.1)

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

    def item_selection(self, item_list, y, x):
        sm_sm_idx = 0
        stored_y = y
        while True:
            for idx, item in enumerate(item_list):
                if sm_sm_idx == idx:
                    self.stdscr.addstr(y, x, str(idx),
                                       self.main_color_r)
                    self.stdscr.addstr(y, x + 5, item,
                                       self.main_color_r)
                else:
                    self.stdscr.addstr(y, x, str(idx),
                                       self.main_color)
                    self.stdscr.addstr(y, x + 5, item,
                                       self.main_color)
                y += 1
            # Reinicializacion del indice
            y = stored_y

            key = self.stdscr.getch()
            if (key == curses.KEY_UP and
                    sm_sm_idx > 0):
                sm_sm_idx -= 1
            elif (key == curses.KEY_DOWN and
                  sm_sm_idx < len(item_list) - 1):
                sm_sm_idx += 1
            elif key == curses.KEY_RIGHT:
                self.stdscr.clear()
                return True, item_list[sm_sm_idx]
            elif key == curses.KEY_LEFT:
                self.stdscr.clear()
                return False, None

    def ermo_agenda(self, mm_idx):
        sm_idx = 0
        self.stdscr.clear()

        while True:
            self.print_menu(mm_idx, False)
            self.print_submenu(self.agenda_submenu, sm_idx)
            sm_key = self.stdscr.getch()

            # Actualizacion del submenu index
            if (sm_key == curses.KEY_LEFT and
                    sm_idx > 0):
                sm_idx -= 1
            elif (sm_key == curses.KEY_RIGHT and
                  sm_idx < len(self.agenda_submenu) - 1):
                sm_idx += 1

            # Navegacion
            if (sm_key == curses.KEY_UP and
                    sm_idx == 0):
                files = os.listdir('data')
                load_state, file = self.item_selection(files, 5, 5)
                file = os.path.join('data', file)
                if load_state:
                    data = pd.read_csv(file, parse_dates=[0])
                    columns = data.columns
                    x_column = 5
                    y_column = 5

                    self.stdscr.addstr(y_column, x_column, columns[0])
                    self.stdscr.addstr(y_column, x_column + 15, columns[1])

            elif sm_key == curses.KEY_DOWN:
                break
