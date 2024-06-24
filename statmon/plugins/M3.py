#!/usr/bin/env python

import os
import sys
import math
import numpy as np

from qtpy import QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR
import PlBase
from error import ERROR

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class M3(Label):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self, parent = None, logger=None):
        super(M3, self).__init__(parent=parent, fs=11.5, width=125, \
                                 height=35, logger=logger)

        #super(AGPlot, self).__init__(*args, **kwargs)
        #M3Canvas.__init__(self, *args, **kwargs)

    def update_m3(self, m3):
        ''' cell = 'TSCV.CellCover'  '''
        self.logger.debug(f'updating m3={m3}')

        if m3 == 0x09:
            self.setText('NS OPT M3 In')
            color = self.normal

        elif m3 == 0x06:
            self.setText('NS IR M3 In')
            color = self.normal

        elif m3 == 0x0a:
            self.setText('M3 Out')
            color = self.normal

        else:
            self.setText('M3 Conflict')
            color = self.alarm

        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))

    def tick(self):
        ''' testing  mode solo '''
        import random
        random.seed()

        indx = random.randrange(0,5)
        m3 = [0x09,0x06,0x0a,'error']

        try:
            m3 = m3[indx]
        except Exception:
            m3 = None

        self.update_m3(m3)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('M3', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow,self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=125
            self.h=25
            self.setup()

        def setup(self):
            self.resize(self.w, self.h)
            self.main_widget = QtWidgets.QWidget(self)

            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)

            m3 =  M3(self.main_widget, logger=logger)

            l.addWidget(m3)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(m3.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("M3 starting..." , 5000)
            #print options

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

    argprs = ArgumentParser(description="CellCover status")


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
