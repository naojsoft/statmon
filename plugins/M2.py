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


class M2(Label):
    ''' telescope 2nd mirror   '''
    def __init__(self, parent=None, logger=None):
        super(M2, self).__init__(parent=parent, fs=16, width=250, \
                                 height=35, logger=logger )

    def update_m2(self,focus):
        ''' focus = STATL.M2_DESCR  '''

        self.logger.debug('focus={}'.format(focus))

        color = self.normal

        if focus.upper()=="M2 UNDEFINED":
            color = self.alarm    

        self.setText(focus)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))

    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()

        indx = random.randrange(0, 5)

        foci = ["Cs Opt M2", "Ns Opt M2", "HSC at M2", 'IR M2', "M2 Undefined"]

        try:
            focus = foci[indx]
        except Exception as e:
            focus = "M2 Undefined"
            print(e)

        self.update_m2(focus)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=250; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0) 
            l.setSpacing(0)
            m2 = M2(parent=self.main_widget, logger=logger)
            l.addWidget(m2)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(m2.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("M2 starting..." , options.interval)

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

