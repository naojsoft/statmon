#
# T. Inagaki
#
from CustomLabel import Label


class InsRot(Label):
    ''' instrument rotator   '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125,
                         height=35, logger=logger )

    def update_insrot(self, insrot, mode):
        self.logger.debug(f'insrot={insrot}, mode={mode}')

        if insrot == self.insrot_free or mode == self.mode_free:
            text = 'InsRot Free'
            color = self.warn
        elif insrot == self.insrot_link and mode == self.mode_link:
            text = 'InsRot Link'
            color = self.normal
        else:
            text = 'InsRot Undefined'
            color = self.alarm

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class InsRotPf(InsRot):
    ''' prime focus rotator  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, logger)

        self.insrot_free = 0x02
        self.insrot_link = 0x01
        self.mode_free = 0x20
        self.mode_link = 0x10

    def update_insrot(self, insrot, mode):
        ''' insrot=TSCV.INSROTROTATION_PF
            mode=TSCV.INSROTMODE_PF
        '''
        super().update_insrot(insrot, mode)


class InsRotCs(InsRot):
    ''' cassegrain rotator  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, logger)

        self.insrot_free = 0x02
        self.insrot_link = 0x01
        self.mode_free = 0x02
        self.mode_link = 0x01

    def update_insrot(self, insrot, mode):
        ''' insrot=TSCV.InsRotRotation
            mode=TSCV.InsRotMode
        '''
        super().update_insrot(insrot, mode)
