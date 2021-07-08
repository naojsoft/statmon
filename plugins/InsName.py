#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR

progname = os.path.basename(sys.argv[0])


class InsName(Label):
    ''' InsName '''
    def __init__(self, parent=None, logger=None):
        super(InsName, self).__init__(parent=parent, fs=13, width=200,\
                                     height=25, align='vcenter', \
                                     weight='normal', logger=logger)

    def update_insname(self, insname):
        ''' insname = FITS.SBR.MAINOBCP '''

        self.logger.debug(f'insname={insname}')

        color = self.normal

        if not insname in ERROR:
            text = f'{insname}'
            #text = '%s %s' %(label.ljust(15), insname.rjust(20))
        else:
            #text = '%s %s' %(label.ljust(15), 'Undefined'.rjust(20))
            text = f"{'Undefined'}"
            color = self.alarm
            self.logger.error(f'error: insname undef. insname={insname}')

        #self.setText('CalProbe: ')
        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))


class InsNameDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(InsNameDisplay, self).__init__(parent)

        self.insname_label = Label(parent=parent, fs=13, width=175,\
                                height=25, align='vcenter', weight='normal', \
                                logger=logger)

        self.insname_label.setText('Instrument')
        self.insname_label.setIndent(15)
        #self.insname_label.setAlignment(QtCore.Qt.AlignVCenter)

        self.insname = InsName(parent=parent, logger=logger)
        self.__set_layout()

    def __set_layout(self):
        objlayout = QtWidgets.QHBoxLayout()
        objlayout.setSpacing(0)
        objlayout.setContentsMargins(0, 0, 0, 0)
        objlayout.addWidget(self.insname_label)
        objlayout.addWidget(self.insname)
        self.setLayout(objlayout)

    def update_insname(self, insname):
        self.insname.update_insname(insname)

    def tick(self):
        ''' testing solo mode '''
        import random
        random.seed()

        indx = random.randrange(0, 9)

        insname = ['HSC', None, 'PFS', 'VGW', "HDS",
                  STATNONE, 'IRD', STATERROR]

        try:
            insname = insname[indx]
        except Exception as e:
            insname = 'SUKA'
            print(e)
        self.update_insname(insname)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w = 450; self.h = 25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            p = InsNameDisplay(parent=self.main_widget, logger=logger)
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
    # note: there are sv/pir plotting, but mode ag uses the same code.
    optprs.add_option("--mode", dest="mode",
                      default='ag',
                      help="Specify a plotting mode [ag | sv | pir | fmos]")

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
