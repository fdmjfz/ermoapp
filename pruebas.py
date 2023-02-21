import curses
import npyscreen

curses.initscr()
curses.curs_set(False)


config_opts = {
    "baud_rate": {
        "command": 'AT+B',
        'opts': [
            1200, 2400, 4800,
            9600, 19200, 38400,
            57600, 115200
        ]
    }
}


def main(stdscr):
    main_form = npyscreen.Form(name="HC12")
    main_form.add(npyscreen.TitleSlider, name="Canle Nº: ", label=True,
                  lowest=1, step=1, out_of=100, value=5)

    main_form.add(npyscreen.TitleMultiLine, name='Baud Rate',
                  rely=5, values=config_opts['baud_rate']['opts'])

    main_form.edit()


curses.wrapper(main)
