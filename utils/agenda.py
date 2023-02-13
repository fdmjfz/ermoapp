import npyscreen
import os
import time
from curses import KEY_LEFT, napms

class agenda(npyscreen.NPSApp):
    def main(self):
        main_form = npyscreen.Form(name="Axenda")

        self.main_options = [
            "Novo arquivo", "Ver", "Engadir rexistro",
            "Eliminar rexistro", "Eliminar arquivo", "Sair"
        ]
        self.existent_file = main_form.add(
            npyscreen.TitleFilenameCombo,
            name="Abrir existente")

        self.selection = main_form.add(npyscreen.TitleSelectOne,
                                       value=[len(self.main_options)-1],
                                       max_height=6,
                                       name="Accion",
                                       values=self.main_options,
                                       scroll_exit=True,
                                       )

        # self.date = self.main_form.add(npyscreen.TitleDateCombo, value="Data:")

        main_form.edit()

    def new_file(self):
        new_file_form = npyscreen.Form(name="Novo arquivo")

        self.new_filename = new_file_form.add(
            npyscreen.TitleFilename, name="Nome:")

        new_file_form.edit()

        txt_name = self.new_filename.value
        filename = 'data/' + txt_name + '.txt'

        if os.path.exists(filename):
            message = f"""
                O arquivo {filename}, xa existe.

                Preme intro pra inicia-la selección.
                """
            write = npyscreen.notify_yes_no(message=message, title='Ollo!', form_color='WARNING')

            if write:
                overwrite = True
            else:
                overwrite = False
        else:
            overwrite = False
            write = True

        if write:
            with open(filename, 'w') as fileout:
                fileout.write('')

            if overwrite:
                message = f"Arquivo {filename} foi sobrescrito."
            else:
                message = f"Arquivo {filename} foi creado."

            npyscreen.notify_wait(message=message, title="Éxito",form_color='VERYGOOD')
        else:
            npyscreen.notify_wait(message='Redirixindo ó menú principal.', title='Saíndo',
                form_color='GOOD')


    def display_txt(self):
        try:
            path = self.existent_file.value
            name = path.rsplit('/')
            name = name[-1]

            with open(path, 'r') as filein:
                text = filein.read()

        except AttributeError:
            message = "Non seleccionaches arquivo."
            npyscreen.notify_wait(message=message, title='Erro',
                form_color='WARNING')
            return

        except UnicodeDecodeError:
            message = "O arquivo seleccionado non pode abrirse coma texto."
            npyscreen.notify_wait(message=message, title='Erro',
                form_color='WARNING')
            return


        display_txt_form = npyscreen.Form(name=name) 
        self.tex = display_txt_form.add(npyscreen.Pager,
                                          values=text.split('\n'),
                                          autowrap=True,
                                          scroll_exit=True,
                                          )
        display_txt_form.edit()

    def add_line(self, line, edit=False):
        try:
            path = self.existent_file.value
            name = path.rsplit('/')
            name = name[-1]

        except AttributeError:
            message = "Non seleccionaches arquivo."
            npyscreen.notify_wait(message=message, title='Erro',
                form_color='WARNING')
            return False

        if edit:
            with open(path, 'a') as fileout:
                fileout.write('\n')
                fileout.write(line)

            with open(path, 'r') as filein:
                lines_count = filein.read().count('\n')

                nl = '\n'
                message = f"""
                    Engadida liña:
                    {line}
                    {nl}
                    Rexistros: {lines_count}
                    """
                npyscreen.notify_wait(message=message, title='Éxito',
                    form_color='VERYGOOD')

        else:
            return True

    def delete_line(self):
        display_txt_form = npyscreen.Form(name="HAHA") 

        path = self.existent_file.value
        name = path.rsplit('/')
        name = name[-1]
        with open(path, 'r') as filein:
            text = filein.read()

        texto = text.split('\n')
        textio = []
        for idx, row in enumerate(texto):
            textio.append(f'{idx}: {row}')

        self.tex = display_txt_form.add(npyscreen.Pager,
                                  values=textio,
                                  autowrap=True,
                                  scroll_exit=True,
                                  )
        display_txt_form.edit()


    def delete_file(self):
        try:
            path = self.existent_file.value
            name = path.rsplit('/')
            name = name[-1]
        except AttributeError:
            message = "Non seleccionaches arquivo."
            npyscreen.notify_wait(message=message, title='Erro',
                form_color='WARNING')
            return

        message = f"""
            De seguro que queres eliminar o arquivo {name} ?

            Preme intro pra inicia-la selección.
            """
        deleted = npyscreen.notify_yes_no(message=message, title='Ollo!', form_color='WARNING')

        if deleted:
            os.remove(path)
            message = f"""
                O arquivo {name} foi eliminado.
                """
            npyscreen.notify_wait(message=message, title="Éxito",form_color='VERYGOOD')
        else:
            npyscreen.notify_wait(message='Redirixindo ó menú principal.', title='Saíndo',
                form_color='GOOD')        


