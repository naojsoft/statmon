#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog

progname = os.path.basename(sys.argv[0])


class Exptime(Label):
    ''' Exposure Time  '''
    def __init__(self, parent=None, logger=None):
        super(Exptime, self).__init__(parent=parent, fs=10, width=110,\
                                     height=25, align='right', \
                                     logger=logger)

        #self.setIndent(55)
        self.setIndent(10)
        #self.setAlignment(QtCore.Qt.AlignVCenter)
    def update_exptime(self, exptime):
        ''' exptime = TSCV.AGExpTime | TSCV.SVExpTime
        '''
        self.logger.debug(f'exptime={exptime}')

        color=self.normal

        try:
            text = '{0:.0f} ms :Exp'.format(exptime)
        except Exception as e:
            text = '{0} :Exp'.format('Undefined')
            color = self.alarm
        finally:
            self.__set_text(text, color)

    def clear(self):
        text = ''
        color = self.normal
        self.__set_text(text, color)

    def __set_text(self, text, color):
        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))

    def tick(self):
        ''' testing solo mode '''
        import random

        exptime = random.random()*random.randrange(0, 40000)
        self.update_exptime(exptime)

def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w = 110; self.h = 25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            e = Exptime(parent=self.main_widget, logger=logger)
            l.addWidget(e)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(e.tick)
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
