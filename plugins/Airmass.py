#!/usr/bin/env python

import sys
import os
import math

from CustomLabel import Label, QtCore, QtWidgets,  ERROR

from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR

progname = os.path.basename(sys.argv[0])


class Airmass(Label):
    ''' Air mass   '''
    def __init__(self, parent=None, logger=None):
        super(Airmass, self).__init__(parent=parent, fs=10, width=275,\
                                     height=25, align='vcenter', \
                                     weight='bold', logger=logger)

        self.setAlignment(QtCore.Qt.AlignVCenter)

    def get_airmass(self, el):

        #am = None
        try:
            assert 1.0 <= el <=179.0
        except Exception as e:
            self.logger.debug(f'error: airmass el range. {e}')
            am = None
        else:
            zd = 90.0 - el
            rad = math.radians(zd)
            sz = 1.0 / math.cos(rad)
            sz1 = sz - 1.0
            am = sz - 0.0018167 * sz1 - 0.002875 * sz1**2 - 0.0008083 * sz1**3
        finally:
            return am

    def update_airmass(self, el):
        ''' el = TSCS.EL '''

        self.logger.debug(f'airmass el={el}')

        color=self.normal
        airmass = self.get_airmass(el)

        if not airmass in ERROR:
            text = '{0:.2f}'.format(airmass)
        else:
            text = '{0}'.format('Undefined')
            color = self.alarm
            self.logger.error(f'error: airmass={airmass}')

        #self.setText('CalProbe: ')
        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))


class AirmassDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(AirmassDisplay, self).__init__(parent)

        self.airmass_label = Label(parent=parent, fs=10, width=175,\
                                height=25, align='vcenter', weight='bold', \
                                logger=logger)

        self.airmass_label.setText('AirMass')
        self.airmass_label.setIndent(15)

        self.airmass = Airmass(parent=parent, logger=logger)
        self.__set_layout()

    def __set_layout(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.airmass_label)
        layout.addWidget(self.airmass)
        self.setLayout(layout)

    def update_airmass(self, el):
        self.airmass.update_airmass(el)

    def tick(self):
        ''' testing solo mode '''
        import random

        el = random.uniform(-20.0, 200)
        if el < -10 or el > 190:
            el = STATNONE

        self.update_airmass(el)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)

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
            #l.setMargin(0)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            p = AirmassDisplay(parent=self.main_widget, logger=logger)
            l.addWidget(p)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(p.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)
            self.statusBar().showMessage("%s starting..." %options.mode, options.interval)

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

    argprs = ArgumentParser(description="Airmass status")

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
