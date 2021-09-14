#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR

progname = os.path.basename(sys.argv[0])


class Object(Label):
    ''' Object  '''
    def __init__(self, parent=None, logger=None):
        super(Object, self).__init__(parent=parent, fs=13, width=200,\
                                     height=25, align='vcenter', \
                                     weight='bold', logger=logger)

    def update_object(self, obj):
        ''' object = FITS.XXX.OBJECT '''

        self.logger.debug(f'obj={obj}')

        color=self.normal

        if not obj in ERROR:
            #text = '%s %s' %(label.ljust(15), obj.rjust(20))
            text = '{0}'.format(obj)
        else:
            #text = '%s %s' %(label.ljust(15), 'Undefined'.rjust(20))
            text = '{0}'.format('Undefined')
            color = self.alarm
            self.logger.error(f'error: object undef. object={obj}')

        #self.setText('CalProbe: ')
        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))


class ObjectDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(ObjectDisplay, self).__init__(parent)

        self.obj_label = Label(parent=parent, fs=13, width=175,\
                                height=25, align='vcenter', \
                                weight='normal', logger=logger)

        self.obj_label.setText('Object')
        self.obj_label.setIndent(15)
        #self.obj_label.setAlignment(QtCore.Qt.AlignVCenter)

        self.obj = Object(parent=parent, logger=logger)
        self._set_layout()

    def _set_layout(self):
        objlayout = QtWidgets.QHBoxLayout()
        objlayout.setSpacing(0)
        objlayout.setContentsMargins(0, 0, 0, 0)
        objlayout.addWidget(self.obj_label)
        objlayout.addWidget(self.obj)
        self.setLayout(objlayout)

    def update_object(self, obj):
        self.obj.update_object(obj)

    def tick(self):
        ''' testing solo mode '''
        import random
        random.seed()

        indx = random.randrange(0, 9)

        obj = ['FOFOSS', None, 'NAOJ1212', 'M78asfaf', "Unknown",
               STATNONE, 'GINZA', STATERROR]

        try:
            obj = obj[indx]
        except Exception as e:
            obj = 'SUBARU'
            print(e)
        self.update_object(obj)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('object', options)

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
            obj = ObjectDisplay(parent=self.main_widget, logger=logger)
            l.addWidget(obj)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(obj.tick)
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

    argprs = ArgumentParser(description="Object status")

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
