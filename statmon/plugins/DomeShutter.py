#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR
from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR

progname = os.path.basename(sys.argv[0])


class DomeShutter(Label):

    ''' state of the DomeShutter  '''
    def __init__(self, parent=None, logger=None):
        super(DomeShutter, self).__init__(parent=parent, fs=10, width=500, \
                                          height=15, fg='white', bg='black', \
                                          weight='bold', logger=logger )

    def update_dome(self, dome):
        ''' dome=STATL.DOMESHUTTER_POS '''
        self.logger.debug('dome=%s' %(str(dome)))

        if dome in ERROR:
            self.logger.error(f'error: dome={dome}')
            text = 'Dome Shutter Undefined'
            bg = self.alarm
            fg = self.fg
        elif dome == "OPEN": # dome shutter open
            self.logger.debug(f'open dome={dome}')
            text = 'Dome Shutter Open'
            bg = self.fg
            fg = self.normal
        elif dome == "CLOSED": # dome shuuter close
            self.logger.debug('close dome={dome}')
            text = 'Dome Shutter Closed'
            bg = self.bg
            fg = self.fg
        elif not dome : # dome shutter  partial
            self.logger.debug('partial dome={dome}')
            text = 'Dome Shutter Partial'
            bg = self.warn
            fg = self.fg

        self.logger.debug(f'text={text}, fg={fg}, bg={bg}')

        self.setStyleSheet("QLabel {color: %s; background-color: %s}" %(fg, bg))
        self.setText(text)

    def tick(self):
        ''' testing solo mode '''
        self.logger.debug('ticking...')
        import random
        random.seed()

        indx = random.randrange(0,8)
        dome = ["OPEN", None,  "CLOSED", 'Unknown', '', STATNONE, STATERROR]

        try:
            dome = dome[indx]
            self.update_dome(dome)
        except Exception as e:
            self.logger.error(f'error: {e}')
            pass


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=500; self.h=15;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            ds = DomeShutter(parent=self.main_widget, logger=logger)
            l.addWidget(ds)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(ds.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)
            self.statusBar().showMessage("DomeShutter starting..." , options.interval)

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

    argprs = ArgumentParser(description="DomeShutter status")

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
