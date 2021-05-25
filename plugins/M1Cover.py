#!/usr/bin/env python

import os
import sys
import math
import numpy as np

from qtpy import QtWidgets, QtCore, QT_VERSION

if QT_VERSION.startswith('5'):
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
else:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

from error import ERROR
from g2base import ssdlog
import PlBase

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

 
class M1Canvas(FigureCanvas):
    """ M1 Mirror """
    def __init__(self, parent=None, width=3, height=3,  logger=None):

        sub=SubplotParams(left=0.0, right=1, bottom=0, top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white', subplotpars=sub)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        #self.axes.grid(True)

        self.closed_color='black'
        self.open_color='white'
        self.onway_color='orange'
        self.alarm_color='red'

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, \
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        #FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Fixed, \
        #                           QtWidgets.QSizePolicy.Fixed)
        #FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w=250
        self.h=70
        self.logger=logger

        self.init_figure()
  
    def init_figure(self):
        ''' initial drawing '''

        # draw mirror
        m1_kwargs=dict(alpha=0.7, fc=self.closed_color, ec='grey', lw=2) 
        self.m1 = mpatches.Wedge((0.5, 0.4), 0.495, 180, 360, **m1_kwargs) 
        self.axes.add_patch(self.m1)

        # draw text
        self.text=self.axes.text(0.5, 0.5, 'Initializing', va='baseline', \
                                 ha='center', \
                                 transform=self.axes.transAxes, fontsize=13)

        self.axes.axison=False
        self.draw()

    def minimumSizeHint(self):
        return QtCore.QSize(self.w, self.h)

    def sizeHint(self):
         return QtCore.QSize(self.w, self.h)


class M1Cover(M1Canvas):
    
    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):
 
        #super(AGPlot, self).__init__(*args, **kwargs)
        M1Canvas.__init__(self, *args, **kwargs)

    def update_m1cover(self, m1cover, m1cover_onway):
        ''' m1cover = TSCV.M1Cover 
            m1cover_onway = TSCV.M1CoverOnway ''' 

        self.logger.debug('updating m1cover=%s m1_onway=%s' %(str(m1cover), str(m1cover_onway)))  
        self.logger.debug('m1cover type={}'.format(type(m1cover)))  


        try:
            if m1cover in ERROR:
                self.m1.set_facecolor(self.alarm_color)
                self.text.set_text('M1 Cover Undef') 
            elif m1cover_onway in ERROR:
                self.m1.set_facecolor(self.alarm_color)
                self.text.set_text('M1 Cover OnWay Undef') 
            elif m1cover_onway == 0x01: # m1 cover onway-open
                self.m1.set_facecolor(self.onway_color)
                self.text.set_text('M1 Cover OnWay-Open') 
            elif m1cover_onway == 0x02: # m1 cover onway-close
                self.m1.set_facecolor(self.onway_color)
                self.text.set_text('M1 Cover OnWay-Closed') 
            elif (m1cover & 0x5555555555555555555555) == 0x1111111111111111111111:
                self.m1.set_facecolor(self.open_color)
                self.text.set_text('M1 Cover Open') 
            elif (m1cover & 0x5555555555555555555555) == 0x4444444444444444444444:
                self.m1.set_facecolor(self.closed_color)
                self.text.set_text('M1 Cover Closed') 
            else:
                self.m1.set_facecolor(self.onway_color)
                self.text.set_text('M1 Cover Partial') 
        except Exception as e:
            self.logger.error('Error: M1 cover. {}'.format(e))
        
        self.draw()

    def tick(self):
        ''' testing  mode solo '''
        import random  
        random.seed()
 
        indx=random.randrange(0, 4)
        m1cover = [0x1111111111111111111111, 'Unknown',  None, 0x4444444444444444444444]

        indx2=random.randrange(0, 4)
        m1onway = [0x01, 0x03, 0x02, None]
        try:
            m1cover = m1cover[indx]
            m1onway = m1onway[indx2]
        except Exception:
            m1cover=None
            m1onway=None
        finally:
            self.update_m1cover(m1cover, m1onway)

def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('plot', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            QtWidgets.QMainWindow.__init__(self)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=250
            self.h=20
            self.setup()

        def setup(self):
            self.resize(self.w, self.h)
            self.main_widget = QtWidgets.QWidget(self)

            l = QtWidgets.QVBoxLayout(self.main_widget)
            m1 =  M1Cover(self.main_widget, logger=logger)

            l.addWidget(m1)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(m1.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("M1 starting..." , 5000)
            #print options

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

        print("%s profile:" % sys.argv[0])
        profile.run('main(options, args)')

    else:
        main(options, args)
