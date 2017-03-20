#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
#import sip
#sip.setapi('QVariant', 2)
from __future__ import absolute_import
from __future__ import print_function
import os
import sys

from PyQt4 import QtCore, QtGui

from g2base import ssdlog


from ObcpStatus import ObcpDisplay
from TscStatus import TscDisplay
from MonStatus import MonDisplay
from Dummy import Dummy

progname = os.path.basename(sys.argv[0])


class StatusTable(QtGui.QWidget):
    def __init__(self, parent=None, logger=None):
        super(StatusTable, self).__init__(parent) 
        
        self.logger = logger

        self.obcp = ObcpDisplay(monitortime=60000,\
                                timedelta=120, logger=logger)

        self.tscs = TscDisplay(monitortime=10000,\
                               timedelta=10,  label='TSCS', logger=logger)

        self.tscl = TscDisplay(monitortime=10000,\
                               timedelta=10,  label='TSCL', logger=logger)

        self.tscv = TscDisplay(monitortime=60000,\
                               timedelta=120,  label='TSCV', logger=logger)

        self.mon = MonDisplay(monitortime=10000,\
                               timedelta=10,  label='MON', logger=logger)

        self._set_layout()

    def _set_layout(self):
   
        mainlayout = QtGui.QVBoxLayout()        
        mainlayout.setSpacing(1) 
        mainlayout.setMargin(0)

        mainlayout.addWidget(self.obcp)        
        mainlayout.addWidget(self.tscs)        
        mainlayout.addWidget(self.tscl)        
        mainlayout.addWidget(self.tscv)
        mainlayout.addWidget(self.mon)

        mainlayout.addWidget(Dummy(height=700, logger=self.logger))

        self.setLayout(mainlayout)


    def update_statustable(self, obcp, obcp_time1, obcp_time2, obcp_time3, obcp_time4, \
                           obcp_time5, obcp_time6, obcp_time7, obcp_time8, obcp_time9, \
                           tscs_time, tscl_time, tscv_time, mon_time):

        self.logger.debug('updating stat-table...') 

        self.obcp.update_obcp(obcp=obcp, obcp_time1=obcp_time1, obcp_time2=obcp_time2, \
                              obcp_time3=obcp_time3, obcp_time4=obcp_time4, \
                              obcp_time5=obcp_time5, obcp_time6=obcp_time6, \
                              obcp_time7=obcp_time7, obcp_time8=obcp_time8, \
                              obcp_time9=obcp_time9)

        self.tscs.update_tsc(tsc_time=tscs_time)
        self.tscl.update_tsc(tsc_time=tscl_time)
        self.tscv.update_tsc(tsc_time=tscv_time)
        self.mon.update_mon(mon_time=mon_time)

    def tick(self):

        for o in [self.obcp, self.tscs, self.tscl, self.tscv, self.mon]:
            o.tick()


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('telescope', options)


    try:
        qApp = QtGui.QApplication(sys.argv)
        tel =  StatusTable(logger=logger)  
        timer = QtCore.QTimer()
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), tel.tick)
        timer.start(options.interval)
        tel.setWindowTitle("%s" % progname)
        tel.show()
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
    # note: there are sv/pir plotting, but mode ag uses the same code.  
    optprs.add_option("--mode", dest="mode",
                      default='ag',
                      help="Specify a plotting mode [ag | sv | pir | fmos]")

    optprs.add_option("--ins", dest="ins",
                      default='HDS',
                      help="Specify 3 character code of an instrument. e.g., HDS")


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

