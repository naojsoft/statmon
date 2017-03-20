#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import sys
import os

from PyQt4 import QtCore, QtGui

from CustomLabel import Label, ERROR
from g2base import ssdlog

progname = os.path.basename(sys.argv[0])

    
class Threshold(Label):
    ''' Threshold(guiding image)  '''
    def __init__(self, parent=None, logger=None):
        super(Threshold, self).__init__(parent=parent, fs=10, width=85,\
                                     height=25, align='vcenter', \
                                     logger=logger)
 
        self.setIndent(10)

    def update_threshold(self, bottom, ceil):
        ''' bottom = TSCV.AG1_I_BOTTOM | TSCV.SV1_I_BOTTOM
            ceil = TSCV.AG1_I_CEIL | TSCV.SV1_I_CEIL
        '''
        self.logger.debug('bottom=%s ceil=%s' %(str(bottom), str(ceil)))

        color = self.normal

        try:
            text = 'Th: {0:.0f} / {1:.0f}'.format(bottom, ceil)
        except Exception as e:
            text = 'Threshold: {0}'.format('Undefined') 
            color = self.alarm

        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))

    def tick(self):
        ''' testing solo mode '''
        import random  

        bottom = random.randrange(0, 30000)
        ceil = random.randrange(30000, 70000)
        self.update_threshold(bottom, ceil)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtGui.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=170; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtGui.QWidget()
            l = QtGui.QVBoxLayout(self.main_widget)
            l.setMargin(0) 
            l.setSpacing(0)
            t = Threshold(parent=self.main_widget, logger=logger)
            l.addWidget(t)

            timer = QtCore.QTimer(self)
            QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), t.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("threshold starting...", options.interval)

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtGui.QApplication(sys.argv)
        aw = AppWindow()
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

