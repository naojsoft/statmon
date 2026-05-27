#
# T. Inagaki
#
from CustomLabel import Label


class Threshold(Label):
    ''' Threshold(guiding image)  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=10, width=85, height=25,
                         align='vcenter', logger=logger)

        #self.setIndent(10)

    def update_threshold(self, bottom, ceil):
        ''' bottom = TSCV.AG1_I_BOTTOM | TSCV.SV1_I_BOTTOM
            ceil = TSCV.AG1_I_CEIL | TSCV.SV1_I_CEIL
        '''
        self.logger.debug(f'bottom={bottom}, ceil={ceil}')

        color = self.normal

        try:
            text = 'Th: {0:.0f} / {1:.0f}'.format(bottom, ceil)
        except Exception as e:
            text = 'Threshold: {0}'.format('Undefined')
            color = self.alarm

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)
