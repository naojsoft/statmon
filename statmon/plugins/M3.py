#
# T. Inagaki
#
from CustomLabel import Label


class M3(Label):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self, parent = None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=35,
                         logger=logger)

    def update_m3(self, m3):
        ''' cell = 'TSCV.CellCover'  '''
        self.logger.debug(f'updating m3={m3}')

        if m3 == 0x09:
            self.set_text('NS OPT M3 In')
            color = self.normal

        elif m3 == 0x06:
            self.set_text('NS IR M3 In')
            color = self.normal

        elif m3 == 0x0a:
            self.set_text('M3 Out')
            color = self.normal

        else:
            self.set_text('M3 Conflict')
            color = self.alarm

        self.set_color(fg=color, bg=self.bg)
