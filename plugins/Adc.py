#!/usr/bin/env python

import sys
import os

# This is only needed for Python v2 but is harmless for Python v3.
#import sip
#sip.setapi('QVariant', 2)

from CanvasLabel import Canvas, QtCore, QtGui, Qt, ERROR
import ssdlog

progname = os.path.basename(sys.argv[0])

    
class Adc(Canvas):
    ''' Cs/Ns ADC  '''
    def __init__(self, parent=None, logger=None):
        super(Adc, self).__init__(parent=parent, fs=11.5, width=125, height=35, logger=logger )
       
        self.mode_free=0x08
        self.mode_link=0x04

    def __adc_power(self, on_off, mode):
         
        adc_off = 0x02
        adc_on = 0x01

        power = {adc_off: ('ADC Free', self.alarm), \
                 adc_on: self.__adc_mode(mode)}

        try:
            adc, color = power[on_off]
        except KeyError:
            adc = 'ADC On/Off Undef'
            color = self.alarm
        finally:
            return (adc, color)

    def __adc_mode(self, mode):
        link = self.mode_link
        free = self.mode_free
        
        adc = {link: ('ADC Link', self.normal), \
               free: ('ADC Free', self.alarm)}
      
        try:
            adc, color = adc[mode]
        except KeyError:
            adc = 'ADC Mode Undef' 
            color = self.alarm
        finally:
            return (adc, color) 

    def adc(self, on_off, mode, in_out):
        adc_out = 0x10
        adc_in = 0x08

        adc = {adc_out: ('ADC Out', self.normal), \
               adc_in: self.__adc_power(on_off, mode)}

        try:
            adc, color = adc[in_out]
        except KeyError:
            adc = 'ADC In/Out Undef'
            color = self.alarm
        finally:
            return (adc, color)  

    def update_adc(self, on_off, mode, in_out):
        ''' on_off = TSCV.ADCOnOff
            mode = TSCV.ADCMode
            in_out = TSCV.ADCInOut
        '''
        self.logger.debug('on_off=%s mode=%s in_out=%s' %(str(on_off), str(mode), str(in_out)))

        text, color = self.adc(on_off=on_off, mode=mode, in_out=in_out)

        self.setText(QtCore.QString(text))
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" %(color, self.bg))


    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()

        onoffindx=random.randrange(0, 4)
        mindx=random.randrange(0, 4)
        ioindx=random.randrange(0, 4)
        
        findx=random.randrange(0, 16)

        on_off=[0x01, 0x02, '##ERROR##', 0x04 ]
 
        mode=[self.mode_free, self.mode_link, '##ERROR##', self.mode_link]

        in_out=[0x08, 0x10, '##ERROR##', 0x03]

        try:
            on_off=on_off[onoffindx]
            mode=mode[mindx]
            in_out=in_out[ioindx]
            #focus=focus[findx]
        except Exception as e:
            print e
            return
        self.update_adc(on_off=on_off, mode=mode, in_out=in_out)


class AdcPf(Adc):
    ''' Prime ADC '''
    def __init__(self, parent=None, logger=None):
        super(AdcPf, self).__init__(parent, logger)
        self.mode_free = 0x80
        self.mode_link = 0x40

    def update_adc(self, on_off, mode, in_out):
        ''' on_off = TSCV.ADCONOFF_PF
            mode = TSCV.ADCMODE_PF
            in_out = TSCV.ADCInOut
        '''
        super(AdcPf, self).update_adc(on_off, mode, in_out) 


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('insrot', options)
 
    class AppWindow(QtGui.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=125; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtGui.QWidget()
            l = QtGui.QVBoxLayout(self.main_widget)
            l.setMargin(0) 
            l.setSpacing(0)

            if options.mode=='pf':
                adc = AdcPf(parent=self.main_widget, logger=logger)
            else:
                adc = Adc(parent=self.main_widget, logger=logger)
            l.addWidget(adc)

            timer = QtCore.QTimer(self)
            QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), adc.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("%s starting..." %options.mode, options.interval)

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtGui.QApplication(sys.argv)
        aw = AppWindow()
        print 'state'
        #state = State(logger=logger)  
        aw.setWindowTitle("%s" % progname)
        aw.show()
        #state.show()
        print 'show'
        sys.exit(qApp.exec_())

    except KeyboardInterrupt, e:
        logger.warn('keyboard interruption....')
        sys.exit(0)



if __name__ == '__main__':
    # Create the base frame for the widgets

    from optparse import OptionParser
 
    usage = "usage: %prog [options] command [args]"
    optprs = OptionParser(usage=usage, version=('%%prog'))
    
    optprs.add_option("--debug", dest="debug", default=False, action="store_true",
                      help="Enter the pdb debugger on main()")
    optprs.add_option("--display", dest="display", metavar="HOST:N",
                      help="Use X display on HOST:N")
    optprs.add_option("--profile", dest="profile", action="store_true",
                      default=False,
                      help="Run the profiler on main()")
    optprs.add_option("--interval", dest="interval", type='int',
                      default=1000,
                      help="Inverval for plotting(milli sec).")
    # note: there are sv/pir plotting, but mode ag uses the same code.  
    optprs.add_option("--mode", dest="mode",
                      default='cs',
                      help="Specify a plotting mode [pf|cs|ns]")

    ssdlog.addlogopts(optprs)
    
    (options, args) = optprs.parse_args()

    if len(args) != 0:
        optprs.error("incorrect number of arguments")

    if options.display:
        os.environ['DISPLAY'] = options.display

    # Are we debugging this?
    if options.debug:
        import pdb

        pdb.run('main(options, args)')

    # Are we profiling this?
    elif options.profile:
        import profile

        print "%s profile:" % sys.argv[0]
        profile.run('main(options, args)')

    else:
        main(options, args)

