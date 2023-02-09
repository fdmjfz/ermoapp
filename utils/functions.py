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
            'Ayuda', 'Agenda'
        ]
        self.num_pad = [
            "abc", "def", "ghi",
            "jkl", "mno", "pqrs",
            "tuv", "wxyz"
        ]
        self.agenda_menu = [
            "prueba", "praba"
        ]

        self.stdscr = stdscr
        self.title_color = title_color
        self.main_color = main_color
        self.main_color_r = main_color_r
        self.secondary_color = secondary_color
        self.secondary_color_r = secondary_color_r
        self.h, self.w = stdscr.getmaxyx()

        self.stdscr.bkgd(' ', main_color)

    def update_index(self, menu_list, key,
                     index, horizontal=True):
        if horizontal:
            if (key == curses.KEY_LEFT and
                    index > 0):
                index -= 1
            elif (key == curses.KEY_RIGHT and
                  index < len(menu_list) - 1):
                index += 1
        else:
            if (key == curses.KEY_UP and
                    index > 0):
                index -= 1
            elif (key == curses.KEY_DOWN and
                  index < len(menu_list) - 1):
                index += 1

        return index

    def display_navigation(self, menu_list, index,
                           horizontal=True, level=1, scr=None):
        if scr:
            scr = scr
            h, w = scr.getmaxyx()
        else:
            scr = self.stdscr
            w = self.w
            h = self.h

        if horizontal:
            x_sep = w//(len(menu_list) + 1)
            x = x_sep
            for idx, row in enumerate(menu_list):
                y = h - level

                if idx == index:
                    scr.addstr(y, x, row,
                               self.main_color_r)
                else:
                    scr.addstr(y, x, row,
                               self.main_color)
                x += x_sep
        else:
            scr.clear()
            menu_list.sort()
            x = w//3
            y = 1
            list_len = h - y

            # Limitación de rangos
            # Equivalencia idx = longitud - 1
            if index < list_len:
                menu_list = menu_list[:list_len]
            else:
                menu_list = menu_list[index-(list_len-2):index+2]
                index = list_len - 1

            for idx, row in enumerate(menu_list):
                if idx == index:
                    scr.addstr(y + idx, x, str(idx),
                               self.secondary_color_r)
                    scr.addstr(y + idx, x, row,
                               self.secondary_color_r)
                else:
                    scr.addstr(y + idx, x, str(idx),
                               self.secondary_color)
                    scr.addstr(y + idx, x, row,
                               self.secondary_color)
        scr.refresh()

    def ermo_agenda(self):
        x_margin = 20
        y_margin = 10
        agenda_width = self.w - x_margin
        agenda_height = self.h - y_margin
        agenda_x = x_margin//2
        agenda_y = y_margin//2
        agenda_win = self.stdscr.subwin(agenda_height, agenda_width,
                                        agenda_y, agenda_x)

        files = os.listdir('data')
        files_idx = 0
        self.display_navigation(menu_list=files, index=files_idx,
                                horizontal=False, level=1, scr=agenda_win)

        while True:
            key = self.stdscr.getch()
            files_idx = self.update_index(menu_list=files,
                                          key=key, index=files_idx,
                                          horizontal=False)
            self.display_navigation(menu_list=files, index=files_idx,
                                    horizontal=False, level=1, scr=agenda_win)

            agenda_win.addstr(7, 20, files[files_idx])

            if key == curses.KEY_RIGHT:
                filepath = f'/data/{files[files_idx]}'
                data = pd.read_csv(filepath, index=False)

            elif key == curses.KEY_LEFT:
                break

        agenda_win.clear()
