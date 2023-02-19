import serial
import npyscreen
from datetime import datetime
import os


class ermo_hc12:
    def __init__(self, serial_port='/dev/ttyS0', baud_rate=9600,
                 timeout=1):
        self.txt_path = os.path.join('data', 'hc12_messages.txt')

        self.device_id = os.getenv('LOGNAME')
        self.device_type = 'u'

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            timeout=timeout,
        )

        if not os.path.exists(self.txt_path):
            open(self.txt_path, 'w')

    def receive(self, store=False):
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

                if store:
                    self.line_prepender(output)

                return output

    def transmit(self, string):
        if string:
            message = f'{self.device_type}{self.device_id}~' + string
            message = message + '>'
            self.serial.write(bytes(message, encoding='utf-8'))

    def hc12_main_view(self, stdscr):
        main_form = npyscreen.Form(name='HC12')
        a = main_form.add(npyscreen.Pager,
                          autowrap=True,
                          max_height=5,
                          )

        while True:
            message = self.receive(True)

            with open(self.txt_path, 'r') as filein:
                text = filein.read()
            a.values = text.split('\n')

            main_form.display()

    def line_prepender(self, line):
        with open(self.txt_path, 'r+') as fileout:
            content = fileout.read()
            fileout.seek(0, 0)
            fileout.write(line.rstrip('\r\n') + '\n' + content)
