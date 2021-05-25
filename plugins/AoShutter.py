#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog

progname = os.path.basename(sys.argv[0])


class Shutter(Label):
    def __init__(self, parent=None, logger=None):
        super(Shutter, self).__init__(parent=parent, fs=11.5, width=70,\
                                    height=20, logger=logger )

        self.status = {'OPEN': self.alarm, 'CLOSE': self.normal} 
              
 
    def shutter(self, shutter):

        self.logger.debug('shutter=%s' %(str(shutter)))

        try:
            color = self.status[shutter]
            text = shutter
        except Exception: 
            color = self.alarm
            text = 'Undef'

        self.setText(text)
        self.setStyleSheet("QLabel {color: %s; background-color: %s}" \
                            %(color, self.bg))


class AoShutter(QtWidgets.QWidget):
    ''' AO Shutters  '''
    def __init__(self, parent=None, logger=None):
        super(AoShutter, self).__init__(parent)

        self.lwsh_label = Label(parent=parent, fs=11.5, width=50,\
                                 height=20, align='vcenter', weight='normal', \
                                 logger=logger)

        self.hwsh_label = Label(parent=parent, fs=11.5, width=50,\
                                 height=20, align='vcenter', weight='normal', \
                                 logger=logger)


        self.lwsh_label.setText('LWSH:')
        self.lwsh_label.setIndent(2)
        self.hwsh_label.setText('HWSH:')
        self.hwsh_label.setIndent(2)

        self.lwsh = Shutter(parent=parent, logger=logger)
        self.hwsh = Shutter(parent=parent, logger=logger)
        self.logger = logger

        self._set_layout() 

    def _set_layout(self):
        top = QtWidgets.QVBoxLayout()

        lwshHbox = QtWidgets.QHBoxLayout()
        lwshHbox.setSpacing(0) 
        lwshHbox.setContentsMargins(0, 0, 0, 0)
        lwshHbox.addWidget(self.lwsh_label)
        lwshHbox.addWidget(self.lwsh)

        hwshHbox = QtWidgets.QHBoxLayout()
        hwshHbox.setSpacing(0) 
        hwshHbox.setContentsMargins(0, 0, 0, 0)
        hwshHbox.addWidget(self.hwsh_label)
        hwshHbox.addWidget(self.hwsh)

        top.setSpacing(1) 
        top.setContentsMargins(0, 0, 0, 0)
        top.addLayout(lwshHbox)
        top.addLayout(hwshHbox)
        self.setLayout(top)
  
    def update_aoshutter(self, lwsh, hwsh):
        ''' lwsh = AON.LWFS.LASH
            hwsh = AON.HWFS.LASH
        '''

        self.logger.debug('lwsh=%s hwsh=%s' %(str(lwsh), str(hwsh)))
   
        self.lwsh.shutter(lwsh)
        self.hwsh.shutter(hwsh)


    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()

        indx = random.randrange(0, 4) 
        shutter = ['OPEN', 'CLOSE', '##NODATA##']

        try:
            shutter = shutter[indx]
        except Exception as e:
            shutter = None
            print(e)
        self.update_aoshutter(lwsh=shutter, hwsh=shutter)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=125; self.h=60;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            a = AoShutter(parent=self.main_widget, logger=logger)
            l.addWidget(a)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(a.tick)
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

