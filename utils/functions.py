
import npyscreen
import time
from datetime import datetime, timedelta
import pandas as pd
import curses
import serial
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
            'Axuda', 'Axenda', 'HC12'
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

            scr.addstr(y - 1, x - 5, "Elixe un arquivo (^ v)")

            # Limitación de rangos
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

    def sms_keyboard(self, waiting, scr=None):
        if not scr:
            scr = self.stdscr

        scr.addstr(2, 0, "Nova entrada: ")
        scr.refresh()
        waiting = timedelta(seconds=waiting)
        idx = None
        message = str()
        while True:
            key = self.stdscr.getkey()
            if key == 'KEY_BACKSPACE':
                message = message[:-1]
            elif key == 'KEY_DOWN':
                scr.clear()
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
            scr.clear()
            self.stdscr.nodelay(False)
            scr.addstr(2, 0, "Nova entrada: ")
            scr.addstr(2, 14, message)
            scr.refresh()

        return message

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

        while True:
            self.display_navigation(menu_list=files, index=files_idx,
                                    horizontal=False, level=1, scr=agenda_win)
            key = self.stdscr.getch()
            files_idx = self.update_index(menu_list=files,
                                          key=key, index=files_idx,
                                          horizontal=False)
            self.display_navigation(menu_list=files, index=files_idx,
                                    horizontal=False, level=1, scr=agenda_win)

            if key == curses.KEY_RIGHT:
                filepath = f'data/{files[files_idx]}'
                self.display_table(filepath=filepath, scr=agenda_win)

            elif key == curses.KEY_LEFT:
                break

        agenda_win.clear()

    def ermo_hc12(self, waiting):
        ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2)

        x_margin = 20
        y_margin = 10
        hc12_width = self.w - x_margin
        hc12_height = self.h - y_margin
        hc12_x = x_margin//2
        hc12_y = y_margin//2
        hc12_win = self.stdscr.subwin(hc12_height, hc12_width,
                                      hc12_y, hc12_x)
        mensaje = self.sms_keyboard(waiting, hc12_win)
        ser.write(bytes(mensaje, encoding='utf8'))
