#!/usr/bin/env python

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

        self.logger.debug(f'updating tsccontrol. kargs={kargs}')

        try:
            tsclogin = kargs.get('GEN2.TSCLOGINS')
            #tsclogin = tsclogin.replace('%', '')
            self.logger.debug(f'tsc login. {tsclogin}')
            self.tsclogin.update_tsclogin(tsclogin=tsclogin)

            tscmode = kargs.get('GEN2.TSCMODE')
            self.logger.debug(f'tsc mode. {tscmode}')
            self.tscmode.update_tscmode(tscmode=tscmode)
        except Exception as e:
            self.logger.error(f'error: updating tsccontrol. {e}')

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
    from argparse import ArgumentParser

    argprs = ArgumentParser(description="EL status")

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
                      default='ag',
                      help="Specify a plotting mode [ag | sv | pir | fmos]")

    argprs.add_argument("--ins", dest="ins",
                      default='HDS',
                      help="Specify 3 character code of an instrument. e.g., HDS")
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
