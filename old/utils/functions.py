import pandas as pd
import time
from datetime import datetime
from curses.textpad import Textbox
import curses


def lcd_clock(lcd):
    lcd.lcd_clear()

    fecha = datetime.now().strftime('%Y-%m-%d')
    hora = datetime.now().strftime('%H:%M:%S')

    lcd.lcd_display_string(fecha, 1, 0)
    lcd.lcd_display_string(hora, 2, 0)

    time.sleep(1)


def lcd_agenda(lcd, agendaIdx):
    lcd.lcd_clear()

    data = pd.read_csv('data/agenda.csv',
                       parse_dates=[0])

    columns = data.columns.to_list()

    lcd.lcd_display_string(str(columns[0]), 1, 0)
    lcd.lcd_display_string("/", 1, 7)
    lcd.lcd_display_string(str(columns[1]), 1, 9)

    row = data.iloc[agendaIdx].to_list()
    row[0] = row[0].strftime('%y-%m-%d')

    lcd.lcd_display_string(str(row[0]), 2, 0)
    lcd.lcd_display_string("/", 2, 8)
    lcd.lcd_display_string(str(row[1]), 2, 8)

    # time.sleep(1)


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
