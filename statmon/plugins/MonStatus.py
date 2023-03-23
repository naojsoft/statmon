#!/usr/bin/env python

import sys
import os

import time
import datetime
import collections

from qtpy import QtCore
from qtpy import QtWidgets

from TscStatus import StatusTime
from CustomLabel import Label, ERROR
from Dummy import Dummy
from g2base import ssdlog

progname = os.path.basename(sys.argv[0])


class MonDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, monitortime=None, timedelta=None, label=None, logger=None):
        super(MonDisplay, self).__init__(parent)

        self.mon_label = Label(parent=parent, fs=13, width=175,\
                                height=25, align='vcenter', weight='normal', \
                                logger=logger)

        self.mon_label.setText('%s:' %label)
        self.mon_label.setIndent(15)

        self.mon = StatusTime(parent=parent, timedelta=timedelta, logger=logger)
        self._set_layout()

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.mon.monitoring)
        timer.start(monitortime)

    def _set_layout(self):
        objlayout = QtWidgets.QHBoxLayout()
        objlayout.setSpacing(0)
        objlayout.setContentsMargins(0, 0, 0, 0)
        objlayout.addWidget(self.mon_label)
        objlayout.addWidget(self.mon)
        self.setLayout(objlayout)

    def update_mon(self, mon_time):
        ''' mon_time = CONTROLLER's last updated time
        '''
        self.mon.update_statustime(mon_time)


    def tick(self):
        ''' testing solo mode '''
        import random
        random.seed()
        num = random.randrange(0, 9)

        if not num % 5:
            mon_time = '##NODATA##'
        else:
            mon_time = time.time()

        self.update_mon(mon_time=mon_time)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('mon status', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=450; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)

            m = MonDisplay(parent=self.main_widget, monitortime=options.monitortime,\
                           timedelta=options.timedelta, label='MON', logger=logger)
            l.addWidget(m)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(m.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)
            self.statusBar().showMessage("Mon starting...", options.interval)

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

    argprs = ArgumentParser(description="Mon status")

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
    argprs.add_argument("--monitortime", dest="monitortime", type=int,
                      default=10000,
                      help="Monitor status arriving time in every milli secs.")
    argprs.add_argument("--timedelta", dest="timedelta", type=int,
                      default=10,
                      help="Specify time delta btw current and previous status receiving time.")

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
