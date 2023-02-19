import serial


class ermo_hc12:
    def __init__(self, serial_port, baud_rate):
        if not serial_port:
            serial_port = '/dev/ttyS0'
        if not baud_rate:
            baud_rate = 9600

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            timeout=10,
        )

    def receive(self):
        x = ser.read_until(bytes('>', encoding='utf-8'))
        message = x.decode('utf-8')
        message = message.replace('>', '')

        items_list = message.split('~')

        device_info = items_list[0].split(',')
        device_id = device_info[0]
        device_type = device_info[1]

        text = items_list[1]

        if device_type == 'u':
            output = f'{device_id}: {text}'

            return output
