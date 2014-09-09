#!/usr/bin/env python

import os
import sys


from PyQt4 import QtGui, QtCore

from CanvasLabel import Canvas, QtCore, QtGui, Qt, ERROR
from Dummy import Dummy
from DomeffWatt import DomeffWatt
from DomeffVolt import DomeffVolt

import ssdlog
import PlBase
from error import *


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class DomeffDisplay(QtGui.QWidget):
    def __init__(self, parent=None, logger=None):
        super(DomeffDisplay, self).__init__(parent)
   
        self.domeff_label = Canvas(parent=parent, fs=13, width=175,\
                                   height=25, align='vcenter', \
                                   weight='normal', logger=logger)

        self.empty_label = Dummy(height=25, logger=logger)


        self.domeff_label.setText('Domeff')
        self.domeff_label.setIndent(15)

        #self.propid_label.setAlignment(QtCore.Qt.AlignVCenter) 

        self.domeffwatt = DomeffWatt(parent=parent, logger=logger)
        self.domeffvolt = DomeffVolt(parent=parent, logger=logger)
        self.__set_layout() 

    def __set_layout(self):
        hlayout = QtGui.QHBoxLayout()
        hlayout.setSpacing(0) 
        hlayout.setMargin(0)

        vlayout1 = QtGui.QVBoxLayout()
        vlayout1.setSpacing(0) 
        vlayout1.setMargin(0)
        vlayout1.addWidget(self.domeff_label)
        vlayout1.addWidget(self.empty_label)

        vlayout2 = QtGui.QVBoxLayout()
        vlayout2.setSpacing(0) 
        vlayout2.setMargin(0)
        vlayout2.addWidget(self.domeffwatt)
        vlayout2.addWidget(self.domeffvolt)

        hlayout.addLayout(vlayout1)
        hlayout.addLayout(vlayout2)

        #hlayout.addWidget(self.domeff_label)
        #hlayout.addWidget(self.domeffwatt)
        self.setLayout(hlayout)

    def update_domeff(self, ff_a, ff_1b, ff_2b, ff_3b, ff_4b,
                      ff_a_v, ff_1b_v, ff_2b_v, ff_3b_v, ff_4b_v):

        self.domeffwatt.update_watt(ff_a, ff_1b, ff_2b, ff_3b, ff_4b)
        self.domeffvolt.update_volt(ff_a_v, ff_1b_v, ff_2b_v, ff_3b_v, ff_4b_v)

    def tick(self):
        ''' testing solo mode '''
        import random  
  
        indx=random.randrange(0, 5)

        ff_a = (1, 2, 5, None, 1)

        ff_1b, ff_2b, ff_3b, ff_4b = [8, 20, 2, 8]


        v = random.uniform(0, 5)

        ff_a_v = v
        ff_1b_v = '#Error'
        ff_2b_v = ff_3b_v = v 
        ff_4b_v = v


 
        #ff_1b, ff_2b, ff_3b, ff_4b = [None, 1 , 90, '#STATNO#']
        try:
            ff_a = ff_a[indx]
        except Exception:
            pass
        else:  
            self.update_domeff(ff_a, ff_1b, ff_2b, ff_3b, ff_4b,
                               ff_a_v, ff_1b_v, ff_2b_v, ff_3b_v, ff_4b_v)



def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('el', options)
 
    class AppWindow(QtGui.QMainWindow):
        def __init__(self):
            QtGui.QMainWindow.__init__(self)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=450; self.h=55;
            self.setup()

        def setup(self):
            self.resize(self.w, self.h)
            self.main_widget = QtGui.QWidget(self)

            l = QtGui.QVBoxLayout(self.main_widget)
            el = DomeffDisplay(self.main_widget, logger=logger)
            l.addWidget(el)

            timer = QtCore.QTimer(self)
            QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), el.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("windscreen starting..."  ,5000)
            #print options

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtGui.QApplication(sys.argv)
        aw = AppWindow()
        aw.setWindowTitle("%s" % progname)
        aw.show()
        sys.exit(qApp.exec_())

    except KeyboardInterrupt as  e:
        print 'key...board'
        logger.info('keyboard interruption....')
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

        print "%s profile:" % sys.argv[0]
        profile.run('main(options, args)')

    else:
        main(options, args)
