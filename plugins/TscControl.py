#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
#import sip
#sip.setapi('QVariant', 2)
from __future__ import absolute_import
from __future__ import print_function
import os
import sys

from qtpy import QtCore, QtWidgets

from g2base import ssdlog

from TscLogin import TscLoginDisplay
from TscMode import TscModeDisplay

progname = os.path.basename(sys.argv[0])


class TscControlGui(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(TscControlGui, self).__init__(parent)

        self.logger = logger
        self.tsclogin = TscLoginDisplay(logger=logger)
        self.tscmode = TscModeDisplay(logger=logger)

        self.set_layout()

    def set_layout(self):
        mainlayout = QtWidgets.QVBoxLayout()
        mainlayout.setSpacing(1)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(self.tsclogin)
        mainlayout.addWidget(self.tscmode)
        self.setLayout(mainlayout)


class TscControl(TscControlGui):
    def __init__(self, parent=None, logger=None):
        super(TscControl, self).__init__(parent=parent, logger=logger)

    def update_tsccontrol(self, **kargs):

        self.logger.debug('updating tsccontrol. {}'.format(kargs))

        try:
            tsclogin = kargs.get('GEN2.TSCLOGINS')
            #tsclogin = tsclogin.replace('%', '')
            self.logger.debug('tsc login. {}'.format(tsclogin))
            self.tsclogin.update_tsclogin(tsclogin=tsclogin)

            tscmode = kargs.get('GEN2.TSCMODE')
            self.logger.debug('tsc mode. {}'.format(tscmode))
            self.tscmode.update_tscmode(tscmode=tscmode)
        except Exception as e:
            self.logger.error('error: updating tsccontrol. {}'.format(e))

    def tick(self):

        self.tsclogin.tick()
        self.tscmode.tick()


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('tsc_control', options)


    try:
        qApp = QtWidgets.QApplication(sys.argv)
        tc = TscControl(logger=logger)
        timer = QtCore.QTimer()
        timer.timeout.connect(tc.tick)
        timer.start(options.interval)
        tc.setWindowTitle("%s" % progname)
        tc.show()
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
