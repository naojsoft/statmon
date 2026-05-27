#
# T. Inagaki
#
from ginga.gw import Widgets

from CustomLabel import Label


class Stage(Label):
    def __init__(self, parent=None, name=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=20,
                         logger=logger)
        self.name = name

    def update_stage(self, stage):

        self.logger.debug(f'stage={stage}')

        try:
            stage = float(stage)
            assert -0.0001 < stage < 0.0001  # stage=0.0
            text = '%s Out' %self.name
            color = self.normal
            bg = self.bg
        except AssertionError:
            try:
                assert 54.9999 < stage < 55.00001  # stage=55.0
                text = '%s In' %self.name
                color = self.bg
                bg = self.normal
            except AssertionError:
                text = '%s Undef' %self.name
                color = self.alarm
                bg = self.bg
        except Exception as e:
            text = '%s Undef' %self.name
            color = self.alarm
            bg = self.bg
        finally:
            self.set_text(text)
            self.set_color(fg=color, bg=bg)


class Waveplate(Widgets.VBox):
    ''' Waveplate Stage   '''
    def __init__(self, parent=None, logger=None):
        super().__init__()

        self.stage1 = Stage(parent=parent, name='Polarizer', logger=logger)
        self.stage2 = Stage(parent=parent, name='1/2 WP', logger=logger)
        self.stage3 = Stage(parent=parent, name='1/4 WP', logger=logger)
        self.logger = logger

        self._set_layout()

    def _set_layout(self):
        self.set_spacing(1)
        self.set_margins(0, 0, 0, 0)
        self.add_widget(self.stage1)
        self.add_widget(self.stage2)
        self.add_widget(self.stage3)

    def update_waveplate(self, stage1, stage2, stage3):
        ''' stage1=WAV.STG1_PS
            stage2=WAV.STG2_PS
            stage3=WAV.STG3_PS
            #focus = TSCV.FOCUSINFO
        '''
        self.logger.debug(f's1={stage1}, s2={stage2}, s3={stage3}')
        self.stage1.update_stage(stage1)
        self.stage2.update_stage(stage2)
        self.stage3.update_stage(stage3)
