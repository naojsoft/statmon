#
# T. Inagaki
#
from ginga.gw import Widgets

from CustomLabel import Label


class Shutter(Label):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=70, height=20,
                         logger=logger)

        self.status = {'OPEN': self.alarm, 'CLOSE': self.normal}

    def shutter(self, shutter):
        self.logger.debug(f'shutter={shutter}')
        try:
            color = self.status[shutter]
            text = shutter
        except Exception:
            color = self.alarm
            text = 'Undef'

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class AoShutter(Widgets.VBox):
    ''' AO Shutters  '''
    def __init__(self, parent=None, logger=None):
        super().__init__()
        self.set_spacing(1)
        self.set_margins(0, 0, 0, 0)

        self.lwsh_label = Label(parent=parent, fs=11.5, width=50,
                                 height=20, align='vcenter', weight='normal',
                                 logger=logger)

        self.hwsh_label = Label(parent=parent, fs=11.5, width=50,
                                 height=20, align='vcenter', weight='normal',
                                 logger=logger)

        self.lwsh_label.set_text('  LWSH:')
        #self.lwsh_label.setIndent(2)
        self.hwsh_label.set_text('  HWSH:')
        #self.hwsh_label.setIndent(2)

        self.lwsh = Shutter(parent=parent, logger=logger)
        self.hwsh = Shutter(parent=parent, logger=logger)
        self.logger = logger

        self._set_layout()

    def _set_layout(self):
        lwshHbox = Widgets.HBox()
        lwshHbox.set_spacing(0)
        lwshHbox.set_margins(0, 0, 0, 0)
        lwshHbox.add_widget(self.lwsh_label)
        lwshHbox.add_widget(self.lwsh)

        hwshHbox = Widgets.HBox()
        hwshHbox.set_spacing(0)
        hwshHbox.set_margins(0, 0, 0, 0)
        hwshHbox.add_widget(self.hwsh_label)
        hwshHbox.add_widget(self.hwsh)

        self.add_widget(lwshHbox)
        self.add_widget(hwshHbox)

    def update_aoshutter(self, lwsh, hwsh):
        ''' lwsh = AON.LWFS.LASH
            hwsh = AON.HWFS.LASH
        '''

        self.logger.debug(f'lwsh={lwsh}, hwsh={hwsh}')

        self.lwsh.shutter(lwsh)
        self.hwsh.shutter(hwsh)
