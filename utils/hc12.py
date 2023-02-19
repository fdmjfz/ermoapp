import serial
import os


class ermo_hc12:
    def __init__(self, serial_port='/dev/ttyS0', baud_rate=9600):

        self.device_id = os.getenv('LOGNAME')
        self.device_type = 'u'

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            timeout=10,
        )

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

                return output

    def transmit(self, string='0'):
        message = f'{self.device_type}{self.device_id}~' + message
        message = message + '>'
        self.serial.write(bytes(message, encoding='utf-8'))
