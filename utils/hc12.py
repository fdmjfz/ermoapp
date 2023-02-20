import serial
import npyscreen
from datetime import datetime
from curses import KEY_DOWN
import RPi.GPIO as GPIO
import time
import os

TXT_PATH = os.path.join('data', 'hc12_messages.txt')


class ermo_hc12:
    def __init__(self, serial_port='/dev/ttyS0', baud_rate=9600,
                 timeout=1, set_hd12_pin=12):

        self.txt_path = TXT_PATH

        self.device_id = os.getenv('LOGNAME')
        self.device_type = 'u'
        self.set_pin = set_hd12_pin

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            timeout=timeout,
        )

        if not os.path.exists(self.txt_path):
            open(self.txt_path, 'w')

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.set_pin, GPIO.OUT)
        GPIO.output(self.set_pin, 1)

    def receive(self):
        x = self.serial.read_until(bytes('>', encoding='utf-8'))

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

                with open(self.txt_path, 'r+') as fileout:
                    content = fileout.read()
                    fileout.seek(0, 0)
                    fileout.write(output.rstrip('\r\n') + '\n' + content)

                return output

    def receive_continuously(self):
        while True:
            self.receive()

    def transmit(self, string):
        if string:
            message = f'{self.device_type}{self.device_id}~' + string
            message = message + '>'
            self.serial.write(bytes(message, encoding='utf-8'))

    def configure(self):
        GPIO.output(self.set_pin, 0)
        time.sleep(1)

        self.serial.write(bytes('AT', encoding='utf-8'))
        response = self.serial.read_until()
        response = response.decode('utf-8')
        response = response.replace('\r\n', '')

        if response != 'OK':
            GPIO.output(self.set_pin, 1)
            return

        GPIO.output(self.set_pin, 1)
        time.sleep(1)


def hc12_main_view(stdscr):
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

        if key == KEY_DOWN:
            break
        elif key == ord('1'):
            main_form.add(npyscreen.TitleText,
                          title="Mensaxe: ")
            message = main_form.edit()

            stdscr.clear()
            stdscr.addstr(5, 5, str(message.values))
            stdscr.refresh()

        time.sleep(2)

    stdscr.nodelay(False)
    return None
