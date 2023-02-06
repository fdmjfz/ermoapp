import pandas as pd
import time
from datetime import datetime
from curses.textpad import Textbox


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
