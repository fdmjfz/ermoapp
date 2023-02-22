import curses
import threading

from utils import functions, agenda, hc12


curses.initscr()
curses.curs_set(False)

curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)

MAIN_COLOR = curses.color_pair(1)
MAIN_COLOR_R = curses.color_pair(2)
TITLE_COLOR = curses.color_pair(3)
SECONDARY_COLOR = curses.color_pair(4)
SECONDARY_COLOR_R = curses.color_pair(5)


# Background threading
bg_task = threading.Thread(target=hc12.receive_continuously, daemon=True,
                           name='Autoupdate HC12')
bg_task.start()


def main(stdscr):
    mm_idx = 0
    ermo = functions.ermo_fun(stdscr, TITLE_COLOR, MAIN_COLOR,
                              MAIN_COLOR_R, SECONDARY_COLOR,
                              SECONDARY_COLOR_R)
    ermo.intro_animate()

    while True:
        # Inicializacion menu
        ermo.stdscr.box()
        ermo.display_navigation(ermo.menu, mm_idx, True,
                                1)

        mm_key = ermo.stdscr.getch()
        mm_idx = ermo.update_index(menu_list=ermo.menu, key=mm_key,
                                   index=mm_idx, horizontal=True)
        ermo.display_navigation(menu_list=ermo.menu, index=mm_idx,
                                horizontal=True, level=1)

        if mm_key == curses.KEY_UP and mm_idx == 1:
            ermo_agenda = agenda.agenda()
            ermo_agenda.main()

            selection = ermo_agenda.selection.get_selected_objects()[0]
            if selection == "Novo arquivo":
                ermo_agenda.new_file()

            elif selection == "Ver":
                ermo_agenda.display_txt()

            elif selection == "Engadir rexistro":
                checked = ermo_agenda.add_line(line='', edit=False)
                if checked:
                    line = ermo.sms_keyboard(0.5)
                    ermo_agenda.add_line(line=line, edit=True)
            elif selection == "Eliminar rexistro":
                ermo_agenda.delete_line()

            elif selection == "Eliminar arquivo":
                ermo_agenda.delete_file()

            elif selection == "Sair":
                continue

        elif mm_key == curses.KEY_UP and mm_idx == 2:
            hc12.hc12_main_view(ermo)

        elif mm_key == ord('q'):
            break


curses.wrapper(main)
