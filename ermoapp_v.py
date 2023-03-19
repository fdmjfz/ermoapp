from bme280pi import Sensor
import curses
from curses.textpad import Textbox, rectangle
from gpiozero import CPUTemperature, BadPinFactory
from psutil import virtual_memory, cpu_percent
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import serial
import time
import os
import threading

from drawings import draw, sub_draw

START_BAUDRATE = 1200

if not os.path.exists('data'):
    os.mkdir('data')
if not os.path.exists('data/agenda.txt'):
    with open('data/agenda.txt', 'w') as fileout:
        fileout.write('')
if not os.path.exists('data/hc12_messages.txt'):
    with open('data/hc12_messages.txt', 'w') as fileout:
        fileout.write('')


def display_alert(scr, line_list: list, alert_type: str,
                  width: int = 50, height: int = 10):
    y, x = scr.getmaxyx()
    scr.clear()

    ypos = (y // 2) - (height // 2)
    xpos = (x // 2) - (width // 2)

    error_win = scr.subpad(height, width, ypos, xpos)

    if alert_type == 'error':
        error_win.bkgd(' ', ERROR)
        error_win.addstr(1, 1, ' Erro! ')
    elif alert_type == 'success':
        error_win.bkgd(' ', MAIN_COLOR)
        error_win.addstr(1, 1, ' Éxito! ')

    error_win.box()
    error_win.hline(2, 1, '-', width - 2)

    ystart = 3
    for line in line_list:
        error_win.addstr(ystart, 1, line)
        ystart += 1

    error_win.addstr(height - 1, 1, " Preme calquera tecla ")

    error_win.refresh()

    scr.getch()


def telemetry_get_values():
    try:
        cpu_temp = 0
        cpu_temp = CPUTemperature().temperature
        gconfig['cpu_temp']['status'] = 'OK'
    except (Warning, BadPinFactory):
        cpu_temp = 0
        gconfig['cpu_temp']['status'] = 'NOK'

    cpu_use = cpu_percent()
    ram_use = virtual_memory()[2]

    output = {
        'CPU T': str(round(cpu_temp, 1)),
        'CPU %': str(round(cpu_use, 1)),
        'RAM %': str(round(ram_use, 1))
    }
    if cpu_temp <= gconfig['cpu_temp']['warning']:
        gconfig['cpu_temp']['status'] = 'OK'
    else:
        gconfig['cpu_temp']['status'] = 'NOK'

    if cpu_use <= gconfig['cpu_use']['warning']:
        gconfig['cpu_use']['status'] = 'OK'
    else:
        gconfig['cpu_use']['status'] = 'NOK'

    if ram_use <= gconfig['ram_use']['warning']:
        gconfig['ram_use']['status'] = 'OK'
    else:
        gconfig['ram_use']['status'] = 'NOK'

    return output


def display_file_text(stdscr, y, x,
                      filepath, title, subtitle,
                      subinfo=None, remove_line=False):
    with open(filepath, 'r') as filein:
        text = filein.read()

    starty_pad = 5
    pad_height = y - (starty_pad + 3)
    text_win = stdscr.subpad(pad_height, x - 2, starty_pad, 1)

    pady, padx = text_win.getmaxyx()
    padyrange = pady - 3
    padxrange = padx - 2

    text = text.split('\n')
    ftext = []
    for idx, line in enumerate(text):
        str_idx = f'{idx}~ '
        new_padxrange = padxrange - len(str_idx)

        if len(line) > new_padxrange:
            splits = len(line) / new_padxrange
            if not float(splits).is_integer():
                splits = int(splits) + 1

            for i in range(0, splits):
                result = str_idx + \
                    line[i*new_padxrange: (i + 1) * new_padxrange]
                ftext.append(result)

        else:
            ftext.append(str_idx + line)

    start_text = 0
    end_text = padyrange
    while True:
        stdscr.clear()
        stdscr.box()
        # text_win.box()
        info = " <- >> Inicio   ^Arriba v Abaixo "
        stdscr.addstr(y - 1, 2, info)
        if subinfo:
            stdscr.addstr(y - 2, 40, subinfo)

        stdscr.addstr(0, 3, " MENÚ ")
        stdscr.hline(1, 1, 0, x - 2)
        stdscr.addstr(1, 8, f' {title} ')
        stdscr.hline(2, 1, 0, x - 2)
        stdscr.addstr(2, 13, f' {subtitle} ')

        if end_text < len(ftext):
            text_win.addstr(padyrange + 1, 2, '[...]')

        autocounter = 1
        subtext = ftext[start_text: end_text]
        for i in subtext:
            text_win.addstr(autocounter, 1, i)
            autocounter += 1

        text_win.refresh()
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and end_text > padyrange:
            end_text -= 1
        elif key == curses.KEY_DOWN and end_text < len(ftext):
            end_text += 1
        elif key == curses.KEY_LEFT:
            break
        elif key == curses.KEY_RIGHT and remove_line:
            text_win.clear()
            text_win.refresh()
            stdscr.clear()
            stdscr.box()

            stdscr.addstr(0, 3, " MENÚ ")
            stdscr.hline(1, 1, 0, x - 2)
            stdscr.addstr(1, 8, f' {title} ')
            stdscr.hline(2, 1, 0, x - 2)
            stdscr.addstr(2, 13, f' {subtitle} ')

            input_width = 30
            input_height = 3
            input_y = 5
            input_x = 2

            rectangle(stdscr, input_y, input_x,
                      input_y + input_height, input_x + input_width)
            stdscr.addstr(input_y, input_x + 2, ' Escribe o nº de liña: ')
            input_win = stdscr.subwin(input_height - 1, input_width - 2,
                                      input_y + 1, input_x + 1)
            stdscr.addstr(10, 2, 'Pra rematar e engadir preme CTRL + G')
            stdscr.addstr(11, 2, 'Pra sair, preme CTRL + G sen texto')
            stdscr.refresh()

            box = Textbox(input_win)
            box.edit()
            text = box.gather()

            if text == '' or text.replace(' ', '') == 0:
                return

            try:
                idx_rm = int(text)
            except ValueError:
                error_list = ["Ingresa únicamente caracteres numéricos."]
                display_alert(stdscr, error_list, 'error')
                return

            with open(AGENDA_TXT_PATH, "r+") as f:
                lines = f.readlines()
                del lines[idx_rm]
                f.seek(0)
                f.truncate()
                f.writelines(lines)
            return

        start_text = end_text - padyrange


def send_message_display(stdscr, y, x):
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(y - 1, 3, " <- >> Inicio ")

    stdscr.addstr(0, 3, " MENÚ ")
    stdscr.hline(1, 1, 0, x - 2)
    stdscr.addstr(1, 8, ' HC12 ')
    stdscr.hline(2, 1, 0, x - 2)
    stdscr.addstr(2, 13, ' ENVIAR MENSAXE ')

    stdscr.addstr(4, 2, "Elixe o tipo de teclado:")
    stdscr.hline(5, 2, '-', 25)
    stdscr.addstr(6, 2, '1 >> QWERTY')
    stdscr.addstr(7, 2, '2 >> SMS')

    key = stdscr.getch()

    if key == ord('1'):
        stdscr.clear()
        stdscr.addstr(1, 3, " <- >> Inicio ")
        stdscr.box()

        stdscr.addstr(0, 3, " MENÚ ")
        stdscr.hline(1, 1, 0, x - 2)
        stdscr.addstr(1, 8, ' HC12 ')
        stdscr.hline(2, 1, 0, x - 2)
        stdscr.addstr(2, 13, ' ENVIAR MENSAXE ')
        stdscr.hline(3, 1, 0, x - 2)
        stdscr.addstr(3, 18, ' QWERTY ')

        input_width = 60
        input_height = 4
        input_y = 5
        input_x = 2

        rectangle(stdscr, input_y, input_x,
                  input_y + input_height, input_x + input_width)
        stdscr.addstr(input_y, input_x + 2, ' Escribe a mensaxe: ')
        input_win = stdscr.subwin(input_height - 1, input_width - 2,
                                  input_y + 1, input_x + 1)
        stdscr.addstr(10, 2, 'Pra rematar e enviar preme CTRL + G')
        stdscr.addstr(11, 2, 'Pra sair, preme CTRL + G sen texto')
        stdscr.refresh()
        input_win.refresh()
        box = Textbox(input_win)
        box.edit()
        text = box.gather()
        hc12_transmit(text)

    elif key == ord('2'):
        text = sms_keyboard(stdscr, 1, 4, 2)
        hc12_transmit(text)
    elif key == curses.KEY_LEFT:
        return


def receive_continuously():
    while True:
        if GPIO.input(set_pin):
            hc12_receive()
        else:
            time.sleep(2)


def display_hc12_preview(hcw):
    y, x = hcw.getmaxyx()  # x = 30
    starty = 1
    startx = 2

    if gconfig['hc12']['needs_refresh']:
        hcw.clear()
        with open('data/hc12_messages.txt', 'r') as filein:
            text = filein.read()

        gconfig['hc12']['needs_refresh'] = False

        text = text.split('\n')

        text = text[:y-2]

        ypos = starty
        xrange = x - (startx * 2)
        for line in text:
            if ypos >= y - 2:
                hcw.addstr(ypos, startx, ' [...] ')
                return

            if len(line) > xrange:
                linebreaks = float(len(line) / xrange)
                if linebreaks.is_integer():
                    linebreaks = int(linebreaks)
                else:
                    linebreaks = int(linebreaks) + 1

                for subidx in range(0, linebreaks):
                    if ypos >= y - 2:
                        continue
                    subline = line[subidx * xrange: (subidx + 1) * xrange]
                    hcw.addstr(ypos, startx, subline)
                    ypos += 1
            else:
                hcw.addstr(ypos, startx, line)
                ypos += 1


def hc12_transmit(string):
    if string:
        message = f'{device_type}{device_id}~' + string
        hc12_serial.write(bytes(message, encoding='utf-8'))

        output = f'{device_id}: {string}'
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = ts + '@' + output

        with open(HC12_TXT_PATH, 'r+') as fileout:
            content = fileout.read()
            fileout.seek(0, 0)
            fileout.write(output.rstrip('\r\n') + '\n' + content)


def buzzer_alarm(delay):
    GPIO.output(buzzer_pin, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(buzzer_pin, GPIO.LOW)


def hc12_receive():
    x = hc12_serial.readline()

    try:
        message = x.decode('utf-8')
    except UnicodeDecodeError:
        return

    if len(message.rstrip('\x00')) == 0:
        return

    if len(message) > 1 and message.startswith('u'):
        message = message.replace('\n', '')
        items_list = message.split('~')

        device_info = items_list[0]
        device_id = device_info[1:]

        text = items_list[1]

        output = f'{device_id}: {text}'
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = ts + '@' + output

        with open(HC12_TXT_PATH, 'r+') as fileout:
            content = fileout.read()
            fileout.seek(0, 0)
            fileout.write(output.rstrip('\r\n') + '\n' + content)

        gconfig['hc12']['needs_refresh'] = True
        buzzer_alarm(0.1)

        return output


def hc12_get_config():
    params = {
        'channel': {
            'command': 'AT+RC',
            'rstring': 'OK+RC'
        },
        'baudrate': {
            'command': 'AT+RB',
            'rstring': 'OK+B'
        },
        'power': {
            'command': 'AT+RP',
            'rstring': 'OK+RP:'
        },
    }
    baud_rates = [
        1200, 2400, 4800,
        9600, 19200, 38400,
        57600, 115200
    ]

    GPIO.output(set_pin, 0)
    time.sleep(0.5)

    if not gconfig['hc12']['baudrate']:
        for br in baud_rates:
            a = serial.Serial(port=serial_port,
                              baudrate=br,
                              timeout=0.25)
            a.write(bytes('AT+RB', encoding='utf-8'))
            try:
                response = a.read_until()
                response = response.decode(encoding='utf-8')
                response = response.replace('\r\n', '')

            except UnicodeDecodeError:
                continue

            if response.startswith('OK'):
                break

        if response != 'OK+B1200':
            a.write(bytes(f'AT+B{START_BAUDRATE}', encoding='utf-8'))
            br_response = a.read_until().decode('utf-8')
            br_response = br_response.replace('\r\n', '')

            if br_response != f'OK+B{START_BAUDRATE}':
                9/0

        time.sleep(0.1)

        for key in params:
            a.write(bytes(params[key]['command'], encoding='utf-8'))

            response = a.read_until()
            response = response.decode('utf-8')
            response = response.replace('\r\n', '')
            response = response.replace(params[key]['rstring'], '')

            gconfig['hc12'][key] = response
            time.sleep(0.1)

        a.close()
        GPIO.output(set_pin, 1)
        time.sleep(1)

    else:
        for key in params:
            hc12_serial.write(bytes(params[key]['command'], encoding='utf-8'))

            response = hc12_serial.read_until()
            response = response.decode('utf-8')
            response = response.replace('\r\n', '')
            response = response.replace(params[key]['rstring'], '')

            gconfig['hc12'][key] = response
            time.sleep(0.1)


def hc12_command_mode(activate: bool):
    if activate:
        GPIO.output(set_pin, 0)
        time.sleep(1)
    else:
        GPIO.output(set_pin, 1)
        time.sleep(0.9)


def hc12_send_command(command):
    hc12_serial.write(bytes(command, encoding='utf-8'))
    response = hc12_serial.read_until()
    response = response.decode('utf-8')

    response_check = command.replace('AT', 'OK')
    response = response.replace('\r\n', '')

    if response == response_check:
        return response
    else:
        return 'error'


def bme280_get_values():
    try:
        temp = bme280.get_temperature()
        hum = bme280.get_humidity()
        press = bme280.get_pressure()

        output = {
            'T ºC: ': str(round(temp, 1)),
            'H %: ': str(round(hum, 1)),
            'P hPa: ': str(round(press, 1))
        }

        gconfig['bme280']['status'] = 'OK'

    except (OSError, NameError):
        output = {
            'T ºC: ': '',
            'H %: ': '',
            'P hPa: ': ''
        }
        gconfig['bme280']['status'] = 'NOK'

    return output


def display_agenda_preview(aw):
    y, x = aw.getmaxyx()  # x = 30
    starty = 1
    startx = 2

    if gconfig['agenda']['needs_refresh']:
        aw.clear()
        with open('data/agenda.txt', 'r') as filein:
            text = filein.read()
        gconfig['agenda']['needs_refresh'] = False

        text = text.split('\n')

        text = text[:y-2]

        ypos = starty
        xrange = x - (startx * 2)
        for line in text:
            if ypos >= y - 2:
                aw.addstr(ypos, startx, ' [...] ')
                return

            if len(line) > xrange:
                linebreaks = float(len(line) / xrange)
                if linebreaks.is_integer():
                    linebreaks = int(linebreaks)
                else:
                    linebreaks = int(linebreaks) + 1

                for subidx in range(0, linebreaks):
                    if ypos >= y - 2:
                        continue
                    subline = line[subidx * xrange: (subidx + 1) * xrange]
                    aw.addstr(ypos, startx, subline)
                    ypos += 1
            else:
                aw.addstr(ypos, startx, line)
                ypos += 1


def reset_clear(mw, uw, stdscr):
    mw.clear()
    uw.clear()
    stdscr.clear()

    mw.border(*mw_border)
    uw.border(*uw_border)
    uw.addstr(0, 3, ' Estados ')

    stdscr.addstr(maxy - 1, maxx - len(sign) - 1,
                  sign)
    stdscr.hline(1, 1, '=', maxx - 2)
    stdscr.addstr(maxy - 1, 2, "Menú >> 1")
    stdscr.addstr(maxy - 1, 12, '|')
    stdscr.addstr(maxy - 1, 14, "Pechar >> Q")

    mw.refresh()
    uw.refresh()
    stdscr.refresh()


def update_alerts(uw, main_color, hl_color):
    sep = 8
    starty = 1
    startx = 1
    y, x = uw.getmaxyx()

    ymax = y - 2
    autocounter = 0
    xpos = startx
    ypos = starty

    for item in gconfig.keys():
        if gconfig[item]['show']:
            if autocounter == ymax:
                autocounter = 0
                ypos = starty
                xpos += sep

            if gconfig[item]['status'] == 'NOK':
                uw.addstr(ypos, xpos, gconfig[item]['name'],
                          hl_color)
            else:
                uw.addstr(ypos, xpos, gconfig[item]['name'])
            ypos += 1
            autocounter += 1

            uw.refresh()


def sms_keyboard(stdscr, waiting, starty,
                 startx):
    y, x = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(y - 1, 3, " INTRO >> Enviar ")
    stdscr.addstr(y - 1, 24, '|')
    stdscr.addstr(y - 1, 29, ' < >> Borrar ')
    stdscr.addstr(18, 2, 'Pra sair preme INTRO sen texto.')

    stdscr.addstr(0, 3, " MENÚ ")
    stdscr.hline(1, 1, 0, x - 2)
    stdscr.addstr(1, 8, ' HC12 ')
    stdscr.hline(2, 1, 0, x - 2)
    stdscr.addstr(2, 13, ' ENVIAR MENSAXE ')
    stdscr.hline(3, 1, 0, x - 2)
    stdscr.addstr(3, 18, ' SMS ')

    legend_win = stdscr.subwin(7, 21, 10, 2)
    legend_win.border(*sw_border)

    button_start_x = 2
    button_start_y = 1
    button_sep = 6
    autocounter = 0
    button_x = button_start_x
    for button in num_pad:
        if autocounter == 3:
            autocounter = 0
            button_start_y += 2
            button_x = button_start_x

        legend_win.addstr(button_start_y, button_x, button)
        button_x += button_sep
        autocounter += 1
        legend_win.refresh()

    scr = stdscr.subwin(4, 50, starty, startx)

    scr.addstr(1, 1, "Texto: ")
    scr.refresh()
    waiting = timedelta(seconds=waiting)
    idx = None
    message = str()
    while True:
        key_raw = stdscr.getch()
        key = chr(key_raw)
        if key_raw == curses.KEY_LEFT:
            message = message[:-1]
        elif key_raw == 10:
            scr.clear()
            break

        else:
            start_time = datetime.now()
            stdscr.nodelay(True)
            subidx = 0

            while datetime.now() - start_time <= waiting:
                try:
                    new_key = stdscr.getkey()
                except curses.error:
                    new_key = 0

                try:
                    idx = int(key) - 1
                except ValueError:
                    continue

                if new_key == key:
                    subidx += 1
                    start_time = datetime.now()

                if subidx >= len(num_pad[idx]):
                    subidx -= len(num_pad[idx])

                time.sleep(0.1)

            if isinstance(idx, int):
                if (idx >= 0 and idx <= 8):
                    message = message + num_pad[idx][subidx]

        subidx = 0
        scr.clear()
        stdscr.nodelay(False)
        scr.addstr(1, 1, "Texto: ")
        scr.addstr(1, 1 + 7, message)
        scr.refresh()

    if message == '\n' or len(message) == 0:
        return None
    else:
        return message


def display_menu(stdscr):
    y, x = stdscr.getmaxyx()

    stdscr.clear()
    stdscr.box()
    stdscr.addstr(0, 3, " MENÚ ")
    stdscr.addstr(y - 1, 3, " <- >> Inicio ")
    stdscr.nodelay(False)

    win_dict = {}
    winy = 1
    for key in menu_opts:
        idx = 0
        sw_len = len(menu_opts[key]) + 2

        win_dict[key] = stdscr.subpad(sw_len, 40, winy, 2)
        win_dict[key].border(*sw_border)
        win_dict[key].addstr(idx, 1, f" {key} ")

        idx += 1
        for item in menu_opts[key]:
            win_dict[key].addstr(idx, 2, item)
            idx += 1
        idx += 1
        winy += sw_len + 1
        win_dict[key].refresh()

    key = stdscr.getch()
    if key == curses.KEY_LEFT:
        pass
    elif key == ord('1'):
        send_message_display(stdscr, y, x)
    elif key == ord('2'):
        display_file_text(stdscr, y, x,
                          HC12_TXT_PATH, 'HC12', 'VER MENSAXES')
    elif key == ord('3'):
        hc12_configure_display(stdscr, y, x)
    elif key == ord('4'):
        agenda_add_line(stdscr, y, x)
    elif key == ord('5'):
        display_file_text(stdscr, y, x,
                          AGENDA_TXT_PATH, 'AXENDA', 'VER AXENDA')
    elif key == ord('6'):
        display_file_text(stdscr, y, x,
                          AGENDA_TXT_PATH, 'AXENDA', 'ELIMINAR LIÑA',
                          ' > >> Engadir número ', True)

    stdscr.nodelay(True)
    gconfig['agenda']['needs_refresh'] = True
    gconfig['hc12']['needs_refresh'] = True
    gconfig['stdscr']['needs_refresh'] = True


def agenda_add_line(stdscr, y, x):
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(y - 1, 3, " <- >> Inicio ")

    stdscr.addstr(0, 3, " MENÚ ")
    stdscr.hline(1, 1, 0, x - 2)
    stdscr.addstr(1, 8, ' AXENDA ')
    stdscr.hline(2, 1, 0, x - 2)
    stdscr.addstr(2, 13, ' ENGADIR NOVA LIÑA ')

    stdscr.addstr(4, 2, "Elixe o tipo de teclado:")
    stdscr.hline(5, 2, '-', 25)
    stdscr.addstr(6, 2, '1 >> QWERTY')
    stdscr.addstr(7, 2, '2 >> SMS')

    key = stdscr.getch()

    if key == ord('1'):
        stdscr.clear()
        stdscr.addstr(1, 3, " <- >> Inicio ")
        stdscr.box()

        stdscr.addstr(0, 3, " MENÚ ")
        stdscr.hline(1, 1, 0, x - 2)
        stdscr.addstr(1, 8, ' AXENDA ')
        stdscr.hline(2, 1, 0, x - 2)
        stdscr.addstr(2, 13, ' ENGADIR NOVA LIÑA ')
        stdscr.hline(3, 1, 0, x - 2)
        stdscr.addstr(3, 18, ' QWERTY ')

        input_width = 60
        input_height = 5
        input_y = 5
        input_x = 2

        rectangle(stdscr, input_y, input_x,
                  input_y + input_height, input_x + input_width)
        stdscr.addstr(input_y, input_x + 2, ' Escribe a liña: ')
        input_win = stdscr.subwin(input_height - 1, input_width - 2,
                                  input_y + 1, input_x + 1)
        stdscr.addstr(10, 2, 'Pra rematar e engadir preme CTRL + G')
        stdscr.addstr(11, 2, 'Pra sair, preme CTRL + G sen texto')
        stdscr.refresh()
        input_win.refresh()
        box = Textbox(input_win)
        box.edit()
        text = box.gather()

        if text == '' or text.replace(' ', '') == 0:
            return

        with open(AGENDA_TXT_PATH, 'r+') as fileout:
            content = fileout.read()
            fileout.seek(0, 0)
            fileout.write(text.rstrip('\r\n') + '\n' + content)

    elif key == ord('2'):
        text = sms_keyboard(stdscr, 1, 4, 2)
        if text:
            with open(AGENDA_TXT_PATH, 'r+') as fileout:
                content = fileout.read()
                fileout.seek(0, 0)
                fileout.write(text.rstrip('\r\n') + '\n' + content)


def display_main_window(mw):
    y, x = mw.getmaxyx()

    mw.addstr(0, 3, " ERMOAPP ")
    mw.addstr(0, maxx - 30,
              datetime.now().strftime(' %Y-%m-%d, %a. %H:%M:%S '))

    bme280 = bme280_get_values()
    tele_data = telemetry_get_values()

    bme_win = mw.subwin(5, 16, 2, 2)
    bme_win.border(*sw_border)
    bme_win.addstr(0, 1, " BME280 ")
    idx = 1
    for key in bme280.keys():
        bme_win.addstr(idx, 1, key)
        bme_win.addstr(idx, 8, bme280[key])
        idx += 1

    tele_win = mw.subwin(5, 16, 2, 22)
    tele_win.border(*sw_border)
    tele_win.addstr(0, 1, " Sistema ")
    idx = 1
    for key in tele_data.keys():
        tele_win.addstr(idx, 1, key)
        tele_win.addstr(idx, 8, tele_data[key])
        idx += 1

    # Horizontales
    hc12_width = x - 2
    hc12_height = 15
    agenda_width = hc12_width
    agenda_height = hc12_height - 5
    agenda_ypos = y - agenda_height

    hc12_win = mw.subpad(hc12_height, hc12_width,
                         agenda_ypos - hc12_height, 1)
    hc12_win.border(*agenda_border)
    hc12_win.addstr(0, 2, f" {gconfig['hc12']['name']} ")
    display_hc12_preview(hc12_win)

    agenda_win = mw.subpad(agenda_height, agenda_width,
                           agenda_ypos, 1)
    agenda_win.border(*agenda_border)
    agenda_win.addstr(0, 2, f" {gconfig['agenda']['name']} ")
    display_agenda_preview(agenda_win)
    # ==========

    hc12_config_win = mw.subpad(5, 16, 2, 42)
    hc12_config_win.border(*sw_border)
    hc12_config_win.addstr(0, 1, " HC12 Conf. ")
    hc12_config_win.addstr(1, 1, 'Canle: ')
    hc12_config_win.addstr(1, 9, str(gconfig['hc12']['channel']))
    hc12_config_win.addstr(2, 1, 'Baud R: ')
    hc12_config_win.addstr(2, 9, str(gconfig['hc12']['baudrate']))
    hc12_config_win.addstr(3, 1, 'Potnc: ')
    hc12_config_win.addstr(3, 9, str(gconfig['hc12']['power']))

    hc12_config_win.refresh()
    hc12_win.refresh()
    agenda_win.refresh()
    bme_win.refresh()
    tele_win.refresh()
    mw.refresh()


def init_screen(stdscr):
    stdscr.clear()
    ypos = 3
    xpos = 5
    xwidth = maxx - xpos - 1

    title_win = stdscr.subpad(14, xwidth, ypos, xpos)
    title_win.addstr(0, 0, draw)
    subtitle_win = stdscr.subpad(14, xwidth, ypos + 10, xpos)
    subtitle_win.addstr(0, 0, sub_draw)
    stdscr.addstr(maxy - 1, 5, "Preme calquera tecla pra iniciar.")

    subtitle_win.refresh()
    title_win.refresh()
    stdscr.refresh()
    stdscr.getch()


def hc12_configure_display(stdscr, y, x):
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(y - 1, 3, " <- >> Inicio ")

    stdscr.addstr(0, 3, " MENÚ ")
    stdscr.hline(1, 1, 0, x - 2)
    stdscr.addstr(1, 8, ' HC12 ')
    stdscr.hline(2, 1, 0, x - 2)
    stdscr.addstr(2, 13, ' CONFIGURACION DO HC12 ')

    stdscr.addstr(4, 2, "Elixe o parámetro:")
    stdscr.hline(5, 2, '-', 25)
    stdscr.addstr(6, 2, '1 >> Canle')
    stdscr.addstr(7, 2, '2 >> Potencia')

    key = stdscr.getch()
    command = ''

    if key == ord('1'):
        stdscr.clear()
        stdscr.box()
        stdscr.addstr(y - 1, 3, " <- >> Inicio ")

        stdscr.addstr(0, 3, " MENÚ ")
        stdscr.hline(1, 1, 0, x - 2)
        stdscr.addstr(1, 8, ' HC12 ')
        stdscr.hline(2, 1, 0, x - 2)
        stdscr.addstr(2, 13, ' CONFIGURACION DO HC12 ')
        stdscr.hline(3, 1, 0, x - 2)
        stdscr.addstr(3, 18, ' CANLE ')

        input_width = 6
        input_height = 3
        input_y = 5
        input_x = 2

        rectangle(stdscr, input_y, input_x,
                  input_y + input_height, input_x + input_width)

        stdscr.addstr(input_y, input_x + 2, ' Nº: ')
        input_win = stdscr.subwin(input_height - 1, input_width - 2,
                                  input_y + 1, input_x + 1)
        stdscr.addstr(10, 2, 'Ingresa valores entre 1-127')
        stdscr.addstr(11, 2, 'Pra rematar e enviar preme CTRL + G')
        stdscr.addstr(
            12, 2, 'Pra saír sen enviar, preme CTRL+ G co cadro baleiro.')
        stdscr.refresh()
        input_win.refresh()
        box = Textbox(input_win)
        box.edit()
        text = box.gather()

        if len(text.replace(' ', '')) == 0:
            return

        try:
            text = int(text)
        except ValueError:
            error_list = ["Ingresa únicamente caracteres numéricos."]
            display_alert(stdscr, error_list, 'error')
            return
        if text not in range(1, 128):
            error_list = []
            error_list.append('Canle fóra de rango.')
            error_list.append('Rango válido entre 1 e 127.')
            display_alert(stdscr, error_list, 'error')
            return

        text = str(text)
        while len(text) < 3:
            text = '0' + text

        command = 'AT+C' + text

    elif key == ord('2'):
        powers = [
            '-1dBm', '2 dBm', '5 dBm',
            '8 dBm', '11 dBm', '14 dBm',
            '17 dBm', '20 dBm'
        ]
        stdscr.clear()
        stdscr.box()
        stdscr.addstr(y - 1, 3, " <- >> Inicio ")

        stdscr.addstr(0, 3, " MENÚ ")
        stdscr.hline(1, 1, 0, x - 2)
        stdscr.addstr(1, 8, ' HC12 ')
        stdscr.hline(2, 1, 0, x - 2)
        stdscr.addstr(2, 13, ' CONFIGURACION DO HC12 ')
        stdscr.hline(3, 1, 0, x - 2)
        stdscr.addstr(3, 18, ' POTENCIA ')
        stdscr.addstr(4, 2, "Elixe a potencia de transmisión:")
        stdscr.hline(5, 2, '-', 32)

        starty = 6

        for idx, row in enumerate(powers):
            idx += 1
            stdscr.addstr(starty, 2, str(idx))
            stdscr.addstr(starty, 4, '>>')
            stdscr.addstr(starty, 7, row)
            starty += 1

        stdscr.refresh()
        sub_key = stdscr.getch()

        if sub_key == curses.KEY_LEFT:
            return

        try:
            sub_key = int(chr(sub_key))
        except ValueError:
            error_list = ["Ingresa únicamente caracteres numéricos."]
            display_alert(stdscr, error_list, 'error')
            return
        if sub_key not in range(1, 9):
            error_list = []
            error_list.append('Canle fóra de rango.')
            error_list.append('Rango válido entre 1 e 8.')
            display_alert(stdscr, error_list, 'error')
            return

        command = f'AT+P{sub_key}'

    elif key == curses.KEY_LEFT:
        return

# Actualizar y enviar comandos
# ============================
    if len(command) <= 3:
        return

    hc12_command_mode(True)
    response = hc12_send_command(command)

    if response == 'error':
        display_alert(stdscr, ['Non se cambiou o parámetro.'], 'error')

    else:
        message_list = []
        message_list.append('Parámetro cambiado.')
        message_list.append(f'Resposta: {response}')
        display_alert(stdscr, message_list, 'success')
        hc12_get_config()

    hc12_command_mode(False)


gconfig = {
    'hc12': {
        'name': 'HC12',
        'status': None,
        'needs_refresh': True,
        'show': True,
        'baudrate': None,
        'channel': None,
        'power': None,
    },
    'bme280': {
        'name': 'BME280',
        'status': None,
        'show': True,
    },
    'cpu_temp': {
        'name': 'CPU T',
        'status': None,
        'warning': 50,
        'show': True,
    },
    'cpu_use': {
        'name': 'CPU %',
        'status': None,
        'warning': 75,
        'show': True,
    },
    'ram_use': {
        'name': 'RAM %',
        'status': None,
        'warning': 75,
        'show': True,
    },
    'agenda': {
        'name': 'AXENDA',
        'status': None,
        'show': False,
        'needs_refresh': True,
    },
    'stdscr': {
        'name': None,
        'status': None,
        'show': False,
        'needs_refresh': True,
    },
}
sign = 'V1.0.0  ErmoLab'
maxy = 50  # / None (dinamico)
maxx = 60  # / None (dinamico)
menu_opts = {
    'HC12': [
        '1 >> Enviar mensaxe',
        '2 >> Ver mensaxes',
        '3 >> Configuración',
    ],
    'AXENDA': [
        '4 >> Engadir nova liña',
        '5 >> Ver axenda',
        '6 >> Borrar liña existente',
    ]
}
num_pad = [
    " 1", "abc2", "def3",
    "ghi4", "jkl5", "mno6",
    "pqrs7", "tuv8", "wxyz9"
]


mw_border = [' ', ' ', 0, 0, 0, 0, 0, 0]
uw_border = [' ', ' ', 0, 0, 0, 0, 0, 0]
sw_border = ['|', '|', '-', '-', 0, 0, 0, 0]
agenda_border = [0, 0, 0, 0, ' ', ' ', ' ', ' ']
HC12_TXT_PATH = os.path.join('data', 'hc12_messages.txt')
AGENDA_TXT_PATH = os.path.join('data', 'agenda.txt')
serial_port = '/dev/ttyS0'
timeout = 2
device_type = 'u'
device_id = os.getenv('USER')
set_pin = 12
buzzer_pin = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(buzzer_pin, GPIO.OUT, initial=0)
GPIO.setup(set_pin, GPIO.OUT, initial=1)
time.sleep(0.1)

hc12_get_config()


try:
    bme280 = Sensor()
    gconfig['bme280']['status'] = 'OK'
except (PermissionError, OSError):
    gconfig['bme280']['status'] = 'NOK'


try:
    hc12_serial = serial.Serial(port=serial_port,
                                baudrate=gconfig['hc12']['baudrate'],
                                timeout=0.4)

    gconfig['hc12']['status'] = 'OK'
except serial.SerialException:
    gconfig['hc12']['status'] = 'NOK'


curses.initscr()
curses.curs_set(False)
curses.noecho()

if maxy and maxx:
    maxy, maxx = maxy, maxx
else:
    maxy, maxx = curses.LINES, curses.COLS

curses.resize_term(maxy, maxx)

curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

MAIN_COLOR = curses.color_pair(1)
MAIN_COLOR_R = curses.color_pair(2)
WARNING = curses.color_pair(3)
ERROR = curses.color_pair(4)

bg_task = threading.Thread(target=receive_continuously, daemon=True,
                           name='Autoupdate HC12')
bg_task.start()


def main(stdscr):
    # INICIALIZACION
    stdscr.attron(MAIN_COLOR)
    init_screen(stdscr)

    mw_limit = (maxy - 1) - 5
    main_window = stdscr.subpad(mw_limit, curses.COLS,
                                0, 0)
    under_window = stdscr.subpad(5, maxx,
                                 mw_limit, 0)

    stdscr.nodelay(True)
    while True:
        if gconfig['stdscr']['needs_refresh']:
            reset_clear(main_window, under_window, stdscr)
            gconfig['stdscr']['needs_refresh'] = False

        key = stdscr.getch()

        update_alerts(under_window, MAIN_COLOR, WARNING)
        display_main_window(main_window)

        if key == ord('1'):
            display_menu(stdscr)
        elif key == ord('q'):
            break

        stdscr.refresh()
        time.sleep(1)

    stdscr.nodelay(False)


curses.wrapper(main)
hc12_serial.close()
