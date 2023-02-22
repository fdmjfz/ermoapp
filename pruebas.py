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
    'power': {
        'command': 'AT+P',
        'opts': {
            '-01dBm': 1, '+02dBm': 2, '+05dBm': 3,
            '+08dBm': 4, '+11dBm': 5, '+14dBm': 6,
            '+17dBm': 7, '+20dBm': 8
        }
    },
    'channel': {
        'command': 'AT+C'
    },
    'sleep': 'AT+SLEEP'
}


def main(stdscr):
    main_form = npyscreen.Form(name="HC12",
                               _contained_widget_height=5)
    report = configure(True)

    channel = main_form.add(npyscreen.TitleSlider, name="Canle Nº: ", label=True,
                            lowest=1, step=1, out_of=100, value=report['channel'])

    power = main_form.add(npyscreen.TitleSelectOne, name='Potencia',
                          max_height=8, scroll_exit=True, rely=5,
                          values=[i for i in config_opts['power']
                                  ['opts'].keys()],
                          value=[config_opts['power']
                                 ['opts'][report['power']] - 1],
                          max_width=29,
                          )

    sleep = main_form.add(npyscreen.Button, name='Apagar')

    main_form.edit()

    channel_set = int(channel.get_value())
    power_set = power.get_values()[power.get_value()[0]]
    power_set = config_opts['power']['opts'][power_set]
    sleep_set = sleep.value

    channel_set = str(channel_set)
    while len(channel_set) < 3:
        channel_set = '0' + channel_set
    channel_command = config_opts['channel']['command'] + channel_set

    power_command = config_opts['power']['command'] + str(power_set)

    commands = [channel_command, power_command]
    if sleep_set is True:
        commands.append('AT+SLEEP')

    stdscr.clear()
    stdscr.addstr(5, 5, str(commands))
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(main)
