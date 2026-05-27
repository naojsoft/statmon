#
# T. Inagaki
#
from CustomLabel import Label, ERROR


class Focus(Label):
    ''' telescope focus  '''

    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=18, width=250, height=35,
                         frame=True, linewidth=1,  logger=logger)

    def update_focus(self,focus, alarm):
        ''' focus = STATL.FOC_DESR
            alarm = TSCV.FOCUSALARM '''

        self.logger.debug(f'focus={focus} alarm={alarm}')

        color = self.normal
        text = focus

        if text.upper()=="FOCUS UNDEFINED":
            color = self.alarm

        try:
            if alarm & 0x40:
                text = 'Focus Changing'
                color = self.alarm
            if alarm & 0x80:
                text = 'Focus Conflict'
                color = self.alarm
                self.logger.error('error: focus in conflict with rot/adc')
        except TypeError:
            text = 'Focus Undefined'
            color = self.alarm
            self.logger.error(f'error: focusalarm undef. focusinfo={focus} focusalarm={alarm}')

        self.set_color(fg=color, bg=self.bg)
        self.set_text(text)
