import curses
import npyscreen

curses.initscr()
curses.curs_set(False)


def configure(status=False):
    if status:
        report = {'baud_rate': 'OK+B9600', 'channel': 'OK+RC024',
                  'power': 'OK+RP:+20dBm', 'mode': 'OK+FU3'}

        report['baud_rate'] = int(report['baud_rate'].replace('OK+B', ''))
        report['channel'] = int(report['channel'].replace('OK+RC', ''))
        report['power'] = report['power'].replace('OK+RP:', '')
        report['mode'] = int(report['mode'].replace('OK+FU', ''))

        return report
    return


config_opts = {
    'baud_rate': {
        'command': 'AT+B',
        'opts': [
            1200, 2400, 4800,
            9600, 19200, 38400,
            57600, 115200
        ]
    },
    'power': {
        'command': 'AT+P',
        'opts': {
            '-1dBm': 1, '+2dBm': 2, '+5dBm': 3,
            '+8dBm': 4, '+11dBm': 5, '+14dBm': 6,
            '+17dBm': 7, '+20dBm': 8
        }
    },
    'mode': {
        'comand': 'AT+FU',
        'opts': [1, 2, 3]
    }
}


def main(stdscr):
    main_form = npyscreen.Form(name="HC12",
                               _contained_widget_height=5)
    report = configure(True)

    channel = main_form.add(npyscreen.TitleSlider, name="Canle Nº: ", label=True,
                            lowest=1, step=1, out_of=100, value=report['channel'])

    baud_rate = main_form.add(npyscreen.TitleSelectOne, name='Baud Rate',
                              rely=5, max_height=5, scroll_exit=True,
                              values=config_opts['baud_rate']['opts'],
                              value=[config_opts['baud_rate']['opts'].index(
                                  report['baud_rate'])],
                              )

    power = main_form.add(npyscreen.TitleSelectOne, name='Potencia',
                          max_height=8, scroll_exit=True,
                          values=[i for i in config_opts['power']
                                  ['opts'].keys()],
                          value=[config_opts['power']
                                 ['opts'][report['power']] - 1],
                          )

    main_form.add(npyscreen.TitleSelectOne, name='FU',
                  max_height=3, scroll_exit=True,
                  values=config_opts['mode']['opts'],
                  value=[config_opts['mode']['opts'].index(report['mode'])]
                  )

    main_form.edit()
    channel_set = channel.get_value()
    baud_rate_set = config_opts['baud_rate']['opts'][baud_rate.get_value()[0]]
    power_set = power.get_values()[power.get_value()[0]]

    stdscr.clear()
    stdscr.addstr(5, 5, str(channel_set))
    stdscr.addstr(6, 5, str(baud_rate_set))
    stdscr.addstr(7, 5, str(power_set))
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(main)
