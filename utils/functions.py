import pandas as pd
import time
from datetime import datetime
import curses

num_pad = [
    "abc", "def", "ghi",
    "jkl", "mno", "pqrs",
    "tuv", "wxyz"
]


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


def sms_keyboard(stdscr, waiting):
    idx = None
    message = str()
    while True:
        key = stdscr.getkey()
        if key == 'KEY_BACKSPACE':
            message = message[:-1]
        elif key == 'q':
            break

        else:
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
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(0, 0, "idx: ")
        stdscr.addstr(0, 8, str(idx))
        stdscr.addstr(1, 0, "subidx: ")
        stdscr.addstr(1, 8, str(subidx))
        stdscr.addstr(2, 0, "messag: ")
        stdscr.addstr(2, 8, message)

    return message
