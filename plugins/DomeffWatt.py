#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import os
import sys


from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.figure import SubplotParams
from matplotlib.artist import Artist

from g2base import ssdlog
import PlBase
from error import *


progname = os.path.basename(sys.argv[0])
progversion = "0.1"

 
class DomeffCanvas(FigureCanvas):
    """ Dome Flat drawing canvas """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):
      
        sub = SubplotParams(left=0, bottom=0, right=1, \
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

        self.x_scale = [0, 1]
        self.y_scale = [0, 1]

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w = 200
        self.h = 25
        #FigureCanvas.resize(self, self.w, self.h)

        self.logger=logger
   
        self.init_figure()
  
    def init_figure(self):
        ''' initial drawing '''

        w = 0.11
        h = 0.6
        label_y = 0.2
        frame_y = 0.1
        common_keys = dict(va='baseline', ha="center", size=13, color=self.normal)       
        kwargs = dict(fc=self.bg, ec=self.normal, lw=1.5)
 
        # 10W Label
        self.axes.text(0.11, label_y, "10W", common_keys)
        
        # 10W frame
        bs = mpatches.BoxStyle("Round4", pad=0.05) 
        self.frame_10w = mpatches.FancyBboxPatch((0.05, frame_y), w, h, \
                                          boxstyle=bs, **kwargs)
        self.axes.add_patch(self.frame_10w)

        # 600W Label
        self.axes.text(0.36, label_y, "600W", common_keys)
       
        # 600# frame
        self.frame_600w = mpatches.FancyBboxPatch((0.3,frame_y), w, h, \
                                          boxstyle=bs, **kwargs)
        self.axes.add_patch(self.frame_600w)
       
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

    def set_10W(self, status, alpha):
        self.frame_10w.set_fc(status)
        self.frame_10w.set_alpha(alpha)

    def set_600W(self, status, alpha):
        self.frame_600w.set_fc(status)
        self.frame_600w.set_alpha(alpha)


class DomeffWatt(DomeffCanvas):
    """ Dome Flat Watt"""
    def __init__(self,*args, **kwargs):
        super(DomeffWatt, self).__init__(*args, **kwargs)

        self.on = 1
        self.off = 2

    def _shift_value(self, val, shift=2):
        ''' default right shift by 2  '''
  
        try:
            #val = int('%s' %(str(val)) , 16)   
            val = val >> shift
        except Exception:
            val = None
        finally:
            return val  

    def _num_of_undef_vals(self, val_set):

        for val in [self.on, self.off]:
            self.logger.debug('val to remove=%s vals=%s' %(str(val), str(val_set)))
            try:
                val_set.remove(val)
                self.logger.debug('removed=%s' %str(val_set))
            except KeyError:
                pass 
        return len(val_set)
 
    def update_watt(self, ff_a, ff_1b, ff_2b, ff_3b, ff_4b):
        ''' note: all values are hex
            ff_a = TSCV.DomeFF_A  
            ff_1b = TSCV.DomeFF_1B
            ff_2b = TSCV.DomeFF_2B
            ff_3b = TSCV.DomeFF_3B
            ff_4b = TSCV.DomeFF_4B
        '''
        self.logger.debug('updating domeff a=%s 1b=%s 2b=%s 3b=%s 4b=%s' %(str(ff_a), str(ff_1b), str(ff_2b), str(ff_3b), str(ff_4b))) 

        # somehow, right shift is required for certain statas aliases
        # before shifting, converting hex to int is also done in this method    
        ff_1b =  self._shift_value(ff_1b)
        ff_2b =  self._shift_value(ff_2b, shift=4)
        ff_4b =  self._shift_value(ff_4b)

        self.logger.debug('shifted value a=%s 1b=%s 2b=%s 3b=%s 4b=%s' %(str(ff_a), str(ff_1b), str(ff_2b), str(ff_3b), str(ff_4b))) 
 
        num_on = [ff_a, ff_1b, ff_2b, ff_3b, ff_4b].count(self.on)     
        self.logger.debug("number of on's=%d" %num_on )

        vals = set([ff_1b, ff_2b, ff_3b, ff_4b])
        num_undef = self._num_of_undef_vals(val_set=vals)       
        self.logger.debug("number of undef's=%d" %num_undef)
        six00W = (ff_1b, ff_2b, ff_3b, ff_4b)  

        self._watt(ff_a, six00W, num_undef, num_on)
        #self.update_voltage()

        self.draw()


    def _watt(self, ff_a, six00W, num_undef, num_on):

        if ff_a == self.on:
            self.set_10W(status=self.normal, alpha=0.3)
            if num_on > self.on:
                self.set_10W(status=self.warn, alpha=1) 
        elif ff_a == self.off:
            self.set_10W(status=self.bg, alpha=1)
        else:
            self.set_10W(status=self.alarm, alpha=1)

        if num_undef: # there is some undef value in 600W, not on or off  
            self.set_600W(status=self.alarm, alpha=1)

        else:  # 600W is either on or off
            if self.on in six00W:
                self.set_600W(status=self.normal, alpha=0.3)

                if num_on > self.on:
                    self.set_600W(status=self.warn, alpha=1)
            else:  #  off 
                self.set_600W(status=self.bg, alpha=1)


class DomeffWattDisplay(QtGui.QWidget):
    def __init__(self, parent=None, logger=None):
        super(DomeffWattDisplay, self).__init__(parent)
   
        self.domeffwatt = DomeffWatt(parent=parent, logger=logger)
        self._set_layout() 

    def _set_layout(self):
        hlayout = QtGui.QHBoxLayout()
        hlayout.setSpacing(0) 
        hlayout.setMargin(0)

        hlayout.addWidget(self.domeffwatt)
        self.setLayout(hlayout)

    def update_domeff_watt(self, ff_a, ff_1b, ff_2b, ff_3b, ff_4b):
        self.domeffwatt.update_watt(ff_a, ff_1b, ff_2b, ff_3b, ff_4b)

    def tick(self):
        ''' testing solo mode '''
        import random  
  
        indx=random.randrange(0, 5)

        ff_a = (1, 2, 5, None, 1)

        ff_1b, ff_2b, ff_3b, ff_4b = [8, 20, 2, 8]
 
        #ff_1b, ff_2b, ff_3b, ff_4b = [None, 1 , 90, '#STATNO#']
        try:
            ff_a = ff_a[indx]
        except Exception:
            pass
        else:  
            self.update_domeff_watt(ff_a, ff_1b, ff_2b, ff_3b, ff_4b)


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
            el = DomeffWattDisplay(self.main_widget, logger=logger)
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
