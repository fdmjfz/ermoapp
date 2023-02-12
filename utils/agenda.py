import npyscreen
import os
from curses import KEY_LEFT


class agenda(npyscreen.NPSApp):
    def main(self):
        main_form = npyscreen.Form(name="Agenda")

        self.files = os.listdir('data')
        self.main_options = [
            "Novo arquivo", "Ver", "Engadir",
            "Eliminar", "Sair"
        ]
        self.existent_file = main_form.add(
            npyscreen.TitleFilenameCombo,
            name="Abrir existente")

        self.selection = main_form.add(npyscreen.TitleSelectOne,
                                       value=[len(self.main_options)-1],
                                       max_height=5,
                                       name="Accion",
                                       values=self.main_options,
                                       scroll_exit=True,
                                       )

        # self.date = self.main_form.add(npyscreen.TitleDateCombo, value="Data:")

        main_form.edit()

    def new_file(self):
        self.file_types = ['.csv', '.txt']

        new_file_form = npyscreen.Form(name="Novo arquivo")

        self.new_filename = new_file_form.add(
            npyscreen.TitleFilename, name="Nome:")

        new_file_form.edit()

        txt_name = self.new_filename.value
        filename = 'data/' + txt_name + '.txt'

        with open(filename, 'w') as fileout:
            fileout.write('')

    def display_txt(self):
        pass
