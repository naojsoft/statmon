#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR

from g2base import ssdlog

progname = os.path.basename(sys.argv[0])

    
class TscLogin(Label):
    ''' TSC Login  '''
    def __init__(self, parent=None, logger=None):
        super(TscLogin, self).__init__(parent=parent, fs=13, width=50,\
                                     height=25, align='left', \
                                     weight='normal', logger=logger)
 
    def update_tsclogin(self, tsclogin):
        ''' tsclogin = GEN2.TSCLOGINS '''
                  
        self.logger.debug('update tsclogin={}'.format(tsclogin))

        color = self.normal

        try:
            assert "OCS" in tsclogin
            text = 'Logged IN({0})'.format(tsclogin)
        except Exception as e:
            text = 'Logged OUT'
            color = self.alarm
            self.logger.warning('warning: gen2 logged out. tsclogin={}'.format(tsclogin))

        #self.setText('CalProbe: ')
        self.setText(text)
        self.setStyleSheet("QLabel {color :%s ; background-color:%s }" \
                           %(color, self.bg))


class TscLoginDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(TscLoginDisplay, self).__init__(parent)
   
        self.tsclogin_label = Label(parent=parent, fs=13, width=30,\
                                height=25, align='vcenter', weight='normal', \
                                logger=logger)

        self.tsclogin_label.setText('TSC Login:')
        self.tsclogin_label.setIndent(15)
        #self.propid_label.setAlignment(QtCore.Qt.AlignVCenter) 

        self.tsclogin = TscLogin(parent=parent, logger=logger)
        self.__set_layout() 

    def __set_layout(self):
        objlayout = QtWidgets.QHBoxLayout()
        objlayout.setSpacing(0) 
        objlayout.setContentsMargins(0, 0, 0, 0)
        objlayout.addWidget(self.tsclogin_label)
        objlayout.addWidget(self.tsclogin)
        self.setLayout(objlayout)

    def update_tsclogin(self, tsclogin):
        self.tsclogin.update_tsclogin(tsclogin)    

    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()

        indx = random.randrange(0, 8)

        tsclogin = ['OCS%,TWS2', None, 'OCS%', '##ERROR##', '', 'TWS2', 'TWS2,OCS%']
 
        try:
            tsclogin = tsclogin[indx]
        except Exception as e:
            tsclogin = 'Undif'
            print(e)
        self.update_tsclogin(tsclogin)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=500; self.h=25;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            tl = TscLoginDisplay(parent=self.main_widget, logger=logger)
            l.addWidget(tl)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(tl.tick)
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

