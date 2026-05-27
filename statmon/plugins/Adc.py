#
# T. Inagaki
#
from CustomLabel import Label


class Adc(Label):
    ''' Cs/Ns ADC  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=35,
                         logger=logger)

        self.adc_out = 16 # hex 0x10
        self.adc_in = 8 # hex 0x08
        self.mode_free = 8 # hex 0x08
        self.mode_link = 4 # hex 0x04
        self.adc_off = 2 # hex 0x02
        self.adc_on = 1 # hex 0x01

    def _adc_power(self, on_off, mode):

        power = {self.adc_off: ('ADC Free', self.alarm), \
                 self.adc_on: self._adc_mode(mode)}

        self.logger.debug(f'Adc power on_off={on_off} mode={mode}')
        try:
            #on_off = int('%s' %on_off, 16)
            text, color = power[on_off]
        except Exception as e:
            self.logger.error(f'error: adc power. {e}')
            text = 'ADC On/Off Undef'
            color = self.alarm
        finally:
            return (text, color)

    def _adc_mode(self, mode):

        adc = {self.mode_link: ('ADC Link', self.normal), \
               self.mode_free: ('ADC Free', self.alarm)}

        self.logger.debug(f'Adc mode mode={mode}')

        try:
            #mode = int('%s' %mode, 16)
            text, color = adc[mode]
        except Exception as e:
            self.logger.error(f'error: adc mode. {e}')
            text = 'ADC Mode Undef'
            color = self.alarm
        finally:
            return (text, color)

    def adc(self, on_off, mode, in_out):

        adc = {self.adc_out: ('ADC Out', self.normal), \
               self.adc_in: self._adc_power(on_off, mode)}

        self.logger.debug(f'Adc on_off={on_off}, mode={mode}, in_out={in_out}')
        try:
            #in_out = int('%s' %in_out, 16)
            text, color = adc[in_out]
        except Exception as e:
            self.logger.error(f'error: updating adc. {e}')
            text = 'ADC In/Out Undef'
            color = self.alarm
        finally:
            return (text, color)

    def update_adc(self, on_off, mode, in_out):
        ''' on_off = TSCV.ADCOnOff
            mode = TSCV.ADCMode
            in_out = TSCV.ADCInOut
        '''
        self.logger.debug(f'on_off={on_off}, mode={mode}, in_out={in_out}')

        text, color = self.adc(on_off=on_off, mode=mode, in_out=in_out)
        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class AdcPf(Adc):
    ''' Prime ADC '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, logger)
        self.mode_free = 128 # hex 0x80
        self.mode_link = 64 # hex 0x40
        # self.adc_off = 0 # hex 0x00
        # self.adc_on = 1 # hex 0x01 # need to check the value

    def update_adc(self, on_off, mode, in_out=8):
        ''' on_off = TSCV.ADCONOFF_PF
            mode = TSCV.ADCMODE_PF
            in_out = 8(always in) #TSCV.ADCInOut
        '''
        super().update_adc(on_off, mode, in_out)
