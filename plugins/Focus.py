#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR
from g2base import ssdlog

import six

if six.PY3:
    long = int

progname = os.path.basename(sys.argv[0])

    
class Focus(Label):
    ''' telescope focus  '''

    def __init__(self, parent=None, logger=None):
        super(Focus, self).__init__(parent=parent, fs=18, width=250, height=35, frame=True, linewidth=1,  logger=logger )

    def update_focus(self,focus, alarm):
        ''' focus = STATL.FOC_DESR 
            alarm = TSCV.FOCUSALARM '''

        self.logger.debug('focus={} alarm={}'.format(focus, alarm))

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
            self.logger.error('error: focusalarm undef. focusinfo=%s focusalarm=%s' %(str(focus),  str(alarm)))

        self.setStyleSheet("QLabel {color :%s; background-color:%s}" \
                           %(color, self.bg) )
        self.setText(text)

    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()

        findx = random.randrange(0, 7)

        foci = ["Cassegrain Optical", 'Prime IR',  "Nasmyth Optical", "Nasmyth IR", "Prime Optical2", 'Cassegrain IR', "Focus Undefined"] 
        
        aindx = random.randrange(0, 6)
        alarm = [0x40,  None, 0x00, 0x80, '##NODATA##', 0x00 ]
        try:
            focus = foci[findx]
            alarm = alarm[aindx]
        except Exception as e:
            focus = "Focus Undefined"
            alarm = 0x40
            print(e)

        self.update_focus(focus, alarm)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w = 250; self.h = 25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            f = Focus(parent=self.main_widget, logger=logger)
            l.addWidget(f)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(f.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("Focus starting..." , options.interval)

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtWidgets.QApplication(sys.argv)
        aw = AppWindow()
        print('state')
        #state = State(logger=logger)  
        aw.setWindowTitle("%s" % progname)
        aw.show()
        #state.show()
        print('show')
        sys.exit(qApp.exec_())

    except KeyboardInterrupt as e:
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

        print("%s profile:" % sys.argv[0])
        profile.run('main(options, args)')

    else:
        main(options, args)

