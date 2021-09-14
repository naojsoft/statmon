#!/usr/bin/env python

import sys
import os

from qtpy import QtCore, QtWidgets

from CustomLabel import Label, ERROR
from g2base import ssdlog

progname = os.path.basename(sys.argv[0])


class Adc(Label):
    ''' Cs/Ns ADC  '''
    def __init__(self, parent=None, logger=None):
        super(Adc, self).__init__(parent=parent, fs=11.5, width=125, height=35, logger=logger )

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
        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" %(color, self.bg))

    def tick(self):
        ''' testing solo mode '''
        import random
        random.seed()

        onoffindx = random.randrange(0, 4)
        mindx = random.randrange(0, 4)
        ioindx = random.randrange(0, 4)

        findx = random.randrange(0, 16)

        on_off = [0x01, 0x02, '##ERROR##', 0x04 ]

        mode = [self.mode_free, self.mode_link, '##ERROR##', self.mode_link]

        in_out = [0x08, 0x10, '##ERROR##', 0x03]

        try:
            on_off = on_off[onoffindx]
            mode = mode[mindx]
            in_out = in_out[ioindx]
            #focus=focus[findx]
        except Exception as e:
            print(e)
            return
        self.update_adc(on_off=on_off, mode=mode, in_out=in_out)


class AdcPf(Adc):
    ''' Prime ADC '''
    def __init__(self, parent=None, logger=None):
        super(AdcPf, self).__init__(parent, logger)
        self.mode_free = 128 # hex 0x80
        self.mode_link = 64 # hex 0x40
        # self.adc_off = 0 # hex 0x00
        # self.adc_on = 1 # hex 0x01 # need to check the value

    def update_adc(self, on_off, mode, in_out=8):
        ''' on_off = TSCV.ADCONOFF_PF
            mode = TSCV.ADCMODE_PF
            in_out = 8(always in) #TSCV.ADCInOut
        '''
        super(AdcPf, self).update_adc(on_off, mode, in_out)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('insrot', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=125; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            #l.setMargin(0)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)

            if options.mode=='pf':
                adc = AdcPf(parent=self.main_widget, logger=logger)
            else:
                adc = Adc(parent=self.main_widget, logger=logger)
            l.addWidget(adc)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(adc.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)
            self.statusBar().showMessage("%s starting..." %options.mode, options.interval)

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtWidgets.QApplication(sys.argv)
        aw = AppWindow()
        aw.setWindowTitle("%s" % progname)
        aw.show()
        sys.exit(qApp.exec_())

    except KeyboardInterrupt as e:
        logger.warn('keyboard interruption....')
        sys.exit(0)



if __name__ == '__main__':
    # Create the base frame for the widgets

    from argparse import ArgumentParser

    argprs = ArgumentParser(description="Telescop ADC status")

    argprs.add_argument("--debug", dest="debug", default=False, action="store_true",
                      help="Enter the pdb debugger on main()")
    argprs.add_argument("--display", dest="display", metavar="HOST:N",
                      help="Use X display on HOST:N")
    argprs.add_argument("--profile", dest="profile", action="store_true",
                      default=False,
                      help="Run the profiler on main()")
    argprs.add_argument("--interval", dest="interval", type=int,
                      default=1000,
                      help="Inverval for plotting(milli sec).")
    # note: there are sv/pir plotting, but mode ag uses the same code.
    argprs.add_argument("--mode", dest="mode",
                      default='cs',
                      help="Specify a plotting mode [pf|cs|ns]")

    ssdlog.addlogopts(argprs)

    (options, args) = argprs.parse_known_args(sys.argv[1:])

    if len(args) != 0:
        argprs.error("incorrect number of arguments")

    if options.display:
        os.environ['DISPLAY'] = options.display

    # Are we debugging this?
    if options.debug:
        import pdb

        pdb.run('main(options, args)')

    # Are we profiling this?
    elif options.profile:
        import profile

        print("%s profile:" % sys.argv[0])
        profile.run('main(options, args)')

    else:
        main(options, args)
