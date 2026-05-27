#
# T. Inagaki
#
from CustomLabel import Label, ERROR


class FocusZ(Label):
    ''' telescope focus z '''
    def __init__(self, parent=None, logger=None):

        super().__init__(parent=parent, fs=14, width=250,
                         height=25, frame=True, linewidth=0.1,
                         logger=logger )

    def update_z(self, z):
        ''' z=TSCL.Z '''

        self.logger.debug(f'z={z}')
        #self.text='Focus: {0:<.04f} mm'.format(z)
        try:
            text = "Focus: %.4f mm" %z
            color = self.normal
        except Exception:
            text = "Focus: Undefined"
            color = self.alarm
            self.logger.error(f'error: focus z undef. z={z}')
        self.set_color(fg=color, bg=self.bg)
        self.set_text(text)
