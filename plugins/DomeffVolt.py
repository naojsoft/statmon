#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import os
import sys

from qtpy import QtWidgets, QtCore, QT_VERSION 

if QT_VERSION.startswith('5'):
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
else:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.figure import SubplotParams
from matplotlib.artist import Artist

from g2base import ssdlog
from error import *
from six.moves import zip


progname = os.path.basename(sys.argv[0])
progversion = "0.1"

 
class DomeffCanvas(FigureCanvas):
    """ Dome Flat drawing canvas """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):
      
        sub=SubplotParams(left=0, bottom=0, right=1, \
                          top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), \
                          facecolor='white', subplotpars=sub)
 
        #self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        #self.fig = Figure(facecolor='white')
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        #self.axes.grid(True)

        self.normal = 'green'
        self.warn = 'orange'
        self.alarm = 'red'
        self.bg = 'white'
        # y axis values. these are fixed values. 
        #self.x_scale=[-0.007, 1.0]
        #self.y_scale=[-0.002,  1.011]

        self.x_scale=[0, 1]
        self.y_scale=[0, 1]

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w = 200
        self.h = 35
        #FigureCanvas.resize(self, self.w, self.h)

        self.logger=logger
   
        self.init_figure()
  
    def init_figure(self):
        ''' initial drawing '''

        w = 0.11
        h = 0.6
        common_keys = dict(va='top', ha="left", size=11)       
        kwargs = dict(fc=self.bg, ec=self.normal, lw=1.5)
  
        '''         
                 col1     col2      col3
           row1  A: 0.0V  1B: 0.0V  3B: 0.0V
           row2           2B: 0.0V  4B: 0.0V

        '''
  
        row1_y = 0.9
        row2_y = 0.35
        col2_x = 0.27
        col3_x = 0.57

        x = 0.07
        d = 0.3
        init = 'Init'

        # 10W A-Volt Label
        self.axes.text(0.01, row1_y, "A:", common_keys, color=self.normal)
        a_volt = self.axes.text(x, row1_y, init, common_keys, color=self.normal)

        # 600W 1B-VOLT  Label
        self.axes.text(col2_x, row1_y, "1B:", common_keys, color=self.normal)
        b1_volt = self.axes.text(x+d, row1_y, init, common_keys, color=self.normal)

        # 600W 2B-VOLT  Label
        self.axes.text(col2_x, row2_y, "2B:", common_keys, color=self.normal)
        b2_volt = self.axes.text(x+d, row2_y, init, common_keys, color=self.normal)

        # 600W 3B-VOLT  Label
        self.axes.text(col3_x, row1_y, "3B:", common_keys, color=self.normal)
        b3_volt = self.axes.text(x+2*d, row1_y, init, common_keys, color=self.normal)

        # 600W 4B-VOLT  Label
        self.axes.text(col3_x, row2_y, "4B:", common_keys, color=self.normal)
        b4_volt = self.axes.text(x+d*2, row2_y, init, common_keys, color=self.normal)

        self.labels = [a_volt, b1_volt, b2_volt, b3_volt, b4_volt]
       
        self.axes.set_ylim(min(self.y_scale), max(self.y_scale))
        self.axes.set_xlim(min(self.x_scale), max(self.x_scale))
        # # disable default x/y axis drawing 
        #self.axes.set_xlabel(False)
        #self.axes.apply_aspect()
        self.axes.set_axis_off()
       
        #self.axes.set_xscale(10)
        #self.axes.axison=False
        self.draw()

    def minimumSizeHint(self):
        return QtCore.QSize(self.w, self.h)

    def sizeHint(self):
         return QtCore.QSize(self.w, self.h)


    def set_voltage(self, label, value, status):
        label.set_text(value)
        label.set_color(status)

    # def set_600W(self, status, alpha):
    #     self.frame_600w.set_fc(status)
    #     self.frame_600w.set_alpha(alpha)


class DomeffVolt(DomeffCanvas):
    """ Dome Flat Voltage"""
    def __init__(self,*args, **kwargs):
        super(DomeffVolt, self).__init__(*args, **kwargs)
 
    def _validate(self, volt):

        try:
            val = '%.1fV' %volt
            res = (val, self.normal)
        except Exception:
            val = 'Undef' 
            res = (val, self.alarm) 

        return res

    def update_volt(self, ff_a_v, ff_1b_v, ff_2b_v, ff_3b_v, ff_4b_v):
        '''
            ff_a_v = TSCV.DomeFF_A_VOL  
            ff_1b_v = TSCV.DomeFF_1B_VOL
            ff_2b_v = TSCV.DomeFF_2B_VOL
            ff_3b_v = TSCV.DomeFF_3B_VOL
            ff_4b_v = TSCV.DomeFF_4B_VOL
        '''
        self.logger.debug('updating domeff a=%s 1b=%s 2b=%s 3b=%s 4b=%s' %(str(ff_a_v), str(ff_1b_v), str(ff_2b_v), str(ff_3b_v), str(ff_4b_v))) 

        volts = [ff_a_v, ff_1b_v, ff_2b_v, ff_3b_v, ff_4b_v]

        for label, volt in zip(self.labels, volts):
            value, status = self._validate(volt)
            self.set_voltage(label, value, status)

        self.draw()


class DomeffVoltDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(DomeffVoltDisplay, self).__init__(parent)
   
        self.domeffvolt = DomeffVolt(parent=parent, logger=logger)
        self.__set_layout() 

    def __set_layout(self):
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(0) 
        hlayout.setContentsMargins(0, 0, 0, 0)

        hlayout.addWidget(self.domeffvolt)
        self.setLayout(hlayout)

    def update_domeff_volt(self, ff_a, ff_1b, ff_2b, ff_3b, ff_4b):
        self.domeffvolt.update_volt(ff_a, ff_1b, ff_2b, ff_3b, ff_4b)

    def tick(self):
        ''' testing solo mode '''
        import random  
  
        v = random.uniform(0, 5)

        ff_a_v = ff_1b_v = ff_2b_v = ff_3b_v = v 
        ff_4b_v = '#STATERROR'

        self.update_domeff_volt(ff_a_v, ff_1b_v, ff_2b_v, ff_3b_v, ff_4b_v)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('el', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            QtWidgets.QMainWindow.__init__(self)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=450; self.h=55;
            self.setup()

        def setup(self):
            self.resize(self.w, self.h)
            self.main_widget = QtWidgets.QWidget(self)

            l = QtWidgets.QVBoxLayout(self.main_widget)
            el = DomeffVoltDisplay(self.main_widget, logger=logger)
            l.addWidget(el)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(el.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("DomeffVolt starting..."  ,5000)
            #print options

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtWidgets.QApplication(sys.argv)
        aw = AppWindow()
        aw.setWindowTitle("%s" % progname)
        aw.show()
        sys.exit(qApp.exec_())

    except KeyboardInterrupt as  e:
        print('key...board')
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

        print("%s profile:" % sys.argv[0])
        profile.run('main(options, args)')

    else:
        main(options, args)
