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
        )
