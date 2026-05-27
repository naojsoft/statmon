#
# T. Inagaki
#

from CustomLabel import Label, ERROR
from g2cam.status.common import STATNONE, STATERROR


class DomeShutter(Label):

    ''' state of the DomeShutter  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=10, width=500,
                         height=20, fg='white', bg='black',
                         weight='bold', logger=logger )

    def update_dome(self, dome):
        ''' dome=STATL.DOMESHUTTER_POS '''
        self.logger.debug('dome=%s' %(str(dome)))

        if dome in ERROR:
            self.logger.error(f'error: dome={dome}')
            text = 'Dome Shutter Undefined'
            bg = self.alarm
            fg = self.fg
        elif dome == "OPEN": # dome shutter open
            self.logger.debug(f'open dome={dome}')
            text = 'Dome Shutter Open'
            bg = self.fg
            fg = self.normal
        elif dome == "CLOSED": # dome shuuter close
            self.logger.debug('close dome={dome}')
            text = 'Dome Shutter Closed'
            bg = self.bg
            fg = self.fg
        elif not dome : # dome shutter  partial
            self.logger.debug('partial dome={dome}')
            text = 'Dome Shutter Partial'
            bg = self.warn
            fg = self.fg

        self.logger.debug(f'text={text}, fg={fg}, bg={bg}')

        self.set_color(fg=fg, bg=bg)
        self.set_text(text)
