#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog

progname = os.path.basename(sys.argv[0])

    
class TscMode(Label):
    ''' TSC Mode  '''
    def __init__(self, parent=None, logger=None):
        super(TscMode, self).__init__(parent=parent, fs=13, width=200,\
                                     height=25, align='vcenter', \
                                     weight='normal', logger=logger)
 
    def update_tscmode(self, tscmode):
        ''' tscmode = GEN2.TSCMODE '''
                  
        self.logger.debug('tscmode={}'.format(tscmode))

        color = self.normal

        if not tscmode in ERROR:
            text = '{0}'.format(tscmode)
        else:
            text = '{0}'.format('Undefined')
            color = self.alarm
            self.logger.error('error: tscmode undef. tscmode={}'.format(tscmode))

        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))


class TscModeDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(TscModeDisplay, self).__init__(parent)
   
        self.tscmode_label = Label(parent=parent, fs=13, width=175,\
                                height=25, align='vcenter', weight='normal', \
                                logger=logger)

        self.tscmode_label.setText('Priority:')
        self.tscmode_label.setIndent(15)
        self.tscmode = TscMode(parent=parent, logger=logger)
        self.__set_layout() 

    def __set_layout(self):
        objlayout = QtWidgets.QHBoxLayout()
        objlayout.setSpacing(0) 
        objlayout.setContentsMargins(0, 0, 0, 0)
        objlayout.addWidget(self.tscmode_label)
        objlayout.addWidget(self.tscmode)
        self.setLayout(objlayout)

    def update_tscmode(self, tscmode):
        self.tscmode.update_tscmode(tscmode)    

    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()

        indx = random.randrange(0, 5)

        tscmode = ['TSC', 'OCS', "Unknown", '##ERROR##']
 
        try:
            tscmode = tscmode[indx]
        except Exception as e:
            tscmode = None
            print(e)
        self.update_tscmode(tscmode)


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
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            tm = TscModeDisplay(parent=self.main_widget, logger=logger)
            l.addWidget(tm)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(tm.tick)
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

