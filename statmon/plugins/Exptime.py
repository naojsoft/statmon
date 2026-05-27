#
# T. Inagaki
#
from CustomLabel import Label, ERROR


class Exptime(Label):
    ''' Exposure Time  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=10, width=110, height=25,
                         align='right', logger=logger)

        #self.setIndent(10)
        #self.setAlignment(QtCore.Qt.AlignVCenter)

    def update_exptime(self, exptime):
        ''' exptime = TSCV.AGExpTime | TSCV.SVExpTime
        '''
        self.logger.debug(f'exptime={exptime}')

        color = self.normal
        try:
            text = '{0:.0f} ms :Exp'.format(exptime)
        except Exception as e:
            text = '{0} :Exp'.format('Undefined')
            color = self.alarm
        finally:
            self.__set_text(text, color)

    def clear(self):
        text = ''
        color = self.normal
        self.__set_text(text, color)

    def __set_text(self, text, color):
        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)
