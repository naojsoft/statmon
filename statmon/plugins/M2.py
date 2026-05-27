#
# T. Inagaki
#
from CustomLabel import Label, ERROR


class M2(Label):
    ''' telescope 2nd mirror   '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=16, width=250, height=35,
                         logger=logger)

    def update_m2(self,focus):
        ''' focus = STATL.M2_DESCR  '''

        self.logger.debug(f'focus={focus}')

        color = self.normal

        if focus.upper() == "M2 UNDEFINED":
            color = self.alarm

        self.set_text(focus)
        self.set_color(color=color, bg=self.bg)
