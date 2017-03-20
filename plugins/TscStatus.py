#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import sys
import os

import time
import datetime
import collections

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.Qt import QMutex, QMutexLocker

from CustomLabel import Label, ERROR
from Dummy import Dummy
from g2base.remoteObjects import remoteObjects as ro
from cfg.INS import INSdata
from g2base import ssdlog

progname = os.path.basename(sys.argv[0])


class StatusTime(Label):
    ''' Status Time  '''
    def __init__(self, parent=None, timedelta=None,  logger=None):
        super(StatusTime, self).__init__(parent=parent, fs=13, width=200,\
                                     height=25, align='vcenter', \
                                     weight='normal', logger=logger)
 
        self.pretime = None
        self.timedelta = timedelta
        self.mutex = QMutex()
        self.logger = logger

    # def monitoring(self):
  
    #     self.logger.debug('monitoring....')
    #     try:
    #         diff = time.time() - self.pretime
    #         self.logger.debug('diff=%f > %f' %(diff, self.timedelta))
    #     except Exception as e:
    #         self.logger.debug('pretime is undefiend. %s' %self.pretime)
    #         if self.pretime is None:
    #             self.update_statustime(stat_time=None)
    #     else: 
    #         if diff > self.timedelta:
    #             self.logger.debug('Stuck. diff=%f' %(diff))
    #             self.logger.debug('calling update_tsc...')
    #             self.update_statustime(stat_time=self.pretime, color=self.alarm)

    def monitoring(self):

        self.logger.debug('calling update_status...')
        self.update_statustime(stat_time=self.pretime)

    def update_statustime(self, stat_time, color=None):
                  
        self.logger.debug('status=%s color=%s' %(str(stat_time), color))

        mutexLocker = QMutexLocker(self.mutex)
        #self.mutex.lock()
 
        try:
            timestamp = datetime.datetime.fromtimestamp(stat_time).strftime('%Y-%m-%d %H:%M:%S')
            fc = self.normal
        except Exception as e:
            timestamp = stat_time = 'Undefined'
            fc = self.alarm
        else: 
            if (time.time()-stat_time) > self.timedelta:
                fc = self.alarm   

        #if color is not None:
        #    fc = color

        self.logger.debug('timestamp=%s color=%s' %(str(timestamp), color))
        self.pretime = stat_time 
        self.setText(timestamp)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(fc, self.bg))
        #self.mutex.unlock()


class TscDisplay(QtGui.QWidget):
    def __init__(self, parent=None, monitortime=None, timedelta=None, label=None, logger=None):
        super(TscDisplay, self).__init__(parent)
   
        self.tsc_label = Label(parent=parent, fs=13, width=175,\
                                height=25, align='vcenter', weight='normal', \
                                logger=logger)

        self.tsc_label.setText('%s:' %label)
        self.tsc_label.setIndent(15)

        self.tsc = StatusTime(parent=parent, timedelta=timedelta, logger=logger)
        self._set_layout() 

        self.logger = logger

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.tsc.monitoring)
        timer.start(monitortime)

    def _set_layout(self):
        objlayout = QtGui.QHBoxLayout()
        objlayout.setSpacing(0) 
        objlayout.setMargin(0)
        objlayout.addWidget(self.tsc_label)
        objlayout.addWidget(self.tsc)
        self.setLayout(objlayout)

    def update_tsc(self, tsc_time):
        ''' time = GEN2.STATUS.TBLTIME.TSCS  or 
            time = GEN2.STATUS.TBLTIME.TSCL  or
            time = GEN2.STATUS.TBLTIME.TSCV
        '''
        self.tsc.update_statustime(stat_time=tsc_time)    

    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()
        num = random.randrange(0, 9)

        if not num % 5:
            tsc_time = '##NODATA##'
        else:
            tsc_time = time.time()
 
        self.update_tsc(tsc_time)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtGui.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=450; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtGui.QWidget()
            l = QtGui.QVBoxLayout(self.main_widget)
            l.setMargin(0) 
            l.setSpacing(0)
            t = TscDisplay(parent=self.main_widget, monitortime=options.monitortime,\
                           timedelta=options.timedelta,  label='TSCS', logger=logger)
            l.addWidget(t)

       
            timer = QtCore.QTimer(self)
            timer.timeout.connect(t.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("TSCS starting...", options.interval)

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtGui.QApplication(sys.argv)
        aw = AppWindow()
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
    optprs.add_option("--monitortime", dest="monitortime", type='int',
                      default=10000,
                      help="Monitor status arriving time in every milli secs.")
    optprs.add_option("--timedelta", dest="timedelta", type='int',
                      default=10,
                      help="Specify time delta btw current and previous status receiving time.")

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


