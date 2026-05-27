#
# T. Inagaki
#
from CustomLabel import Label, ERROR
from g2cam.status.common import STATNONE, STATERROR


class TipChop(Label):
    ''' telescope 2nd mirror   '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=16, width=125,
                         height=35, logger=logger)

    def update_tipchop(self, mode, drive, data, state, focus=None, focus2=None):
        '''
           mode=TSCV.TT_Mode
           drive=TSCV.TT_Drive
           data=TSCV.TT_DataAvail
           chop_state=TSCV.TT_ChopStat
           focus=
           focus2=
        '''

        self.logger.debug(f'mode={mode}, drive={drive}, data={data}, state={state}')
        self.logger.debug(f'focus={focus}, focus2={focus2}')

        color = self.normal

        if (mode in ERROR or drive in ERROR or
            data in ERROR or state in ERROR):
            text = ''
        elif not drive&0x01 and drive&0x02: # not drive on
            text = ''
        elif mode&0x47 == 0x04:  # positon mode is ok
            text = ''
        elif mode&0x47 == 0x02: # tip-tilt mode
            text = 'Tip-Tilt'
            if not data&0x01: # data not available
                color = self.warn
        elif mode&0x47 == 0x01: # chopping mode
            text = 'Chopping'
            # choppig stop/not chopping start/not chopping start ready
            if state&0x02 or (not state&0x05 == 0x05):
                color = self.warn
        else:
            text = 'Tip/Chop Undefined'
            color = self.alarm

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)
