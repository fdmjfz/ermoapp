import serial
import npyscreen
from datetime import datetime
from curses import KEY_DOWN
import RPi.GPIO as GPIO
import time
import os


TXT_PATH = os.path.join('data', 'hc12_messages.txt')
serial_port = '/dev/ttyS0'
baud_rate = 1200
timeout = 1
set_pin = 12
device_type = 'u'
device_id = os.getenv('USER')

CONFIG_OPTS = {
    'power': {
        'command': 'AT+P',
        'opts': {
            '-1dBm': 1, '+2dBm': 2, '+5dBm': 3,
            '+8dBm': 4, '+11dBm': 5, '+14dBm': 6,
            '+17dBm': 7, '+20dBm': 8
        }
    },
    'channel': {
        'command': 'AT+C'
    },
    'sleep': 'AT+SLEEP'
}

serial = serial.Serial(
    port=serial_port,
    baudrate=baud_rate,
    timeout=timeout,
)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(set_pin, GPIO.OUT)
GPIO.output(set_pin, 1)


def receive():
    x = serial.read_until(bytes('>', encoding='utf-8'))

    if len(x) > 0:
        message = x.decode('utf-8')
        message = message.replace('>', '')

        items_list = message.split('~')

        device_info = items_list[0]
        device_type = device_info[0]
        device_id = device_info[1:]

        text = items_list[1]

        if device_type == 'u':
            output = f'{device_id}: {text}'
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            output = ts + '@' + output

            with open(TXT_PATH, 'r+') as fileout:
                content = fileout.read()
                fileout.seek(0, 0)
                fileout.write(output.rstrip('\r\n') + '\n' + content)

            return output


def receive_continuously():
    while True:
        if GPIO.input(set_pin):
            receive()
        else:
            time.sleep(1)


def transmit(string):
    if string:
        message = f'{device_type}{device_id}~' + string
        message = message + '>'
        serial.write(bytes(message, encoding='utf-8'))

        output = f'{device_id}: {string}'
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = ts + '@' + output

        with open(TXT_PATH, 'r+') as fileout:
            content = fileout.read()
            fileout.seek(0, 0)
            fileout.write(output.rstrip('\r\n') + '\n' + content)


def configure(command_list=None):
    GPIO.output(set_pin, 0)
    time.sleep(2)

    serial.write(bytes('AT', encoding='utf-8'))
    response = serial.read_until()
    response = response.decode('utf-8')
    response = response.replace('\r\n', '')

    if response == 'OK':
        if not command_list:
            params = {'channel': 'AT+RC', 'power': 'AT+RP'}
            report = {}

            for param in params:
                serial.write(bytes(params[param], encoding='utf-8'))
                value = serial.read_until().decode('utf-8')
                value = value.replace('\r\n', '')
                report[param] = value

            report['channel'] = int(report['channel'].replace('OK+RC', ''))
            report['power'] = report['power'].replace('OK+RP:', '')

            GPIO.output(set_pin, 1)
            return report
        else:
            for command in command_list:
                serial.write(bytes(command, encoding='utf-8'))
                time.sleep(0.1)
                response = serial.read_until().decode('utf-8')
                response = response.replace('\r\n', '')
                if response != command.replace('AT', 'OK'):
                    9/0

            GPIO.output(set_pin, 1)
            return

    GPIO.output(set_pin, 1)
    serial.baudrate = baud_rate
    time.sleep(1)


def hc12_main_view(stdscr):
    if not os.path.exists(TXT_PATH):
        open(TXT_PATH, 'w')

    name = 'HC12 || 1 Mensaxe QWERTY | 2 Mensaxe SMS | 3 Configuración'
    main_form = npyscreen.Form(name=name)
    a = main_form.add(npyscreen.Pager,
                      autowrap=True,
                      max_height=8,
                      height=10,
                      )

    stdscr.nodelay(True)
    while True:
        key = stdscr.getch()

        with open(TXT_PATH, 'r') as filein:
            text = filein.read()

        a.values = text.split('\n')
        main_form.display()

        message = ''
        time.sleep(1)

        if key == KEY_DOWN:
            break
        elif key == ord('1'):  # QWERTY
            message = main_form.add(npyscreen.TitleText,
                                    name="Mensaxe (preme intro): ")
            main_form.edit()
            message = message.get_value()
            transmit(message)

        elif key == ord('3'):  # CONFIGURE
            stdscr.nodelay(False)
            hc12_config_form = npyscreen.Form(name="HC12")

            report = configure()
            channel = hc12_config_form.add(npyscreen.TitleSlider,
                                           name="Canle Nº: ", label=True,
                                           lowest=1, step=1, out_of=100,
                                           value=report['channel'])

            power = hc12_config_form.add(npyscreen.TitleSelectOne,
                                         name='Potencia', max_height=8,
                                         scroll_exit=True,
                                         values=[
                                             i for i in CONFIG_OPTS[
                                                 'power']['opts'].keys()
                                         ],
                                         value=[
                                             CONFIG_OPTS['power']
                                             ['opts'][report['power']] - 1
                                         ],
                                         )
            sleep = main_form.add(npyscreen.Button, name='Apagar')

            # PREPROCESAMIENTO PARA OBTENER LISTA DE COMANDOS AL HC12
            hc12_config_form.edit()

            channel_set = int(channel.get_value())
            power_set = power.get_values()[power.get_value()[0]]
            power_set = CONFIG_OPTS['power']['opts'][power_set]
            sleep_set = sleep.value

            channel_set = str(channel_set)
            while len(channel_set) < 3:
                channel_set = '0' + channel_set
            channel_command = CONFIG_OPTS['channel']['command'] + channel_set
            power_command = CONFIG_OPTS['power']['command'] + str(power_set)

            command_list = [channel_command, power_command]
            if sleep_set is True:
                command_list.append('AT+SLEEP')

            # ENVIO DE COMANDOS AL HC12
            configure(command_list=command_list)

            stdscr.nodelay(True)

    stdscr.nodelay(False)
    return
