#!/usr/bin/env python

import os
import sys
import math
import numpy as np

from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
from matplotlib.figure import SubplotParams
from matplotlib.artist import Artist

#import matplotlib as mpl

import ssdlog
import PlBase
from error import *

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

 
class AzElCanvas(FigureCanvas):
    """ Windscreen """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):
      
        sub=SubplotParams(left=0.0, bottom=0, right=1, \
                          top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), \
                          facecolor='white', subplotpars=sub)
 
        #self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        #self.fig = Figure(facecolor='white')
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        #self.axes.grid(True)

        self.limit_low=0.0
        self.limit_high=90.0;

        self.alarm_high=89.5
        self.alarm_low=10.0

        self.warn_high=89.0
        self.warn_low=15.0


        self.normal_color='green'
        self.warn_color='orange'
        self.alarm_color='red'

        # y axis values. these are fixed values. 
        #self.x_scale=[-0.007, 1.0]
        #self.y_scale=[-0.002,  1.011]

        self.x_scale=[0, 1]
        self.y_scale=[0, 1]
        self.center = 0.5
        self.new_x = 0.5
        self.new_y = 0.375

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w=250
        self.h=250
        #FigureCanvas.resize(self, self.w, self.h)

        self.logger=logger
   
        self.init_figure()
  
    def init_figure(self):
        ''' initial drawing '''

        # wind direction
        self.wind = self.axes.annotate('', xy=(self.center, self.center+0.4), 
                                 xytext=(self.center, self.center+0.498),
                                 size=29.5, color='b',
                                 arrowprops=dict(arrowstyle="wedge,tail_width=0.7", \
                                                 facecolor='blue', ec="none", \
                                                 alpha=0.5, patchA=None, \
                                                 relpos=(0.0, -0.1)),
                                 horizontalalignment='center')

        # center +
        center_x = Line2D([self.center, self.center], \
                          [self.center, self.center], 
                          alpha=0.1, marker='+', ms=165.0, \
                          mew=1.5, mec=self.normal_color, markevery=(0,1))
        self.axes.add_line(center_x)

        # inner circle
        inner_c = Circle((self.center, self.center), radius=0.25, \
                         fc="white", ec=self.normal_color, lw=0.5, ls='solid')
        self.axes.add_patch(inner_c)

        d_offset=0.2
        directions = {'N':(self.center, self.center+d_offset),\
                      'S':(self.center, self.center-d_offset),\
                      'E':(self.center+d_offset, self.center),\
                      'W':(self.center-d_offset, self.center)}

        # dirctions 
        for key, vals in directions.items():
            self.axes.text(vals[0], vals[1], key, \
                           color='g', ha='center', va='center', \
                           fontsize=18, \
                           transform=self.axes.transAxes)

        # subaru telescope direction
        subaru_radius = 0.125
        # subaru's directions: south 0 , west 90, noroth 180, east 270/-90   
        self.subaru = mpatches.RegularPolygon((self.center, \
                                               self.center-subaru_radius), \
                                               3, subaru_radius, \
                                               orientation=math.pi, \
                                               fc='b', ec='none', alpha=0.5)

        self.axes.add_patch(self.subaru)

        # subaru text        
        self.axes.text(self.center, self.center, 'S', \
                       color='g', ha='center', va='center', \
                       fontsize=30, weight='bold',  \
                       transform=self.axes.transAxes)
        #s_txt.set_rotation(angle)

        # subaru telescope
        subaru = mpatches.Circle((self.center, self.center), \
                                  radius=subaru_radius, \
                                  alpha=1, ec="b", fc='white', lw=2.5)
        self.axes.add_patch(subaru)
  
        # outter circle
        outer_c = Circle((self.center, self.center), radius=0.492, \
                         fc="None", ec=self.normal_color, lw=1.5, ls='solid',
                         transform=self.axes.transAxes )
        self.axes.add_patch(outer_c)

        # telescope elevation
        self.el_kwargs=dict(r=0.5, theta2=180, alpha=0.5, lw=0.5, width=0.25) 
        self.el = mpatches.Wedge((self.center, self.center), theta1=90, \
                                  fc=self.normal_color, ec=self.normal_color, \
                                  **self.el_kwargs) 
        self.axes.add_patch(self.el)

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


class AzEl(AzElCanvas):
    
    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):
 
        #super(AGPlot, self).__init__(*args, **kwargs)
        AzElCanvas.__init__(self, *args, **kwargs)

    def __get_xy(self, degree, sign=1, radius=0):

        rad = math.radians(degree)
        new_x = self.center  + sign * radius * math.sin(rad)
        new_y = self.center  + sign * radius * math.cos(rad)
       
        return (new_x, new_y) 

    def __update_wind_direction(self, direction):

        try:
            b_x, b_y = self.__get_xy(degree=direction, radius=0.498)  
            h_x, h_y = self.__get_xy(degree=direction, radius=0.4)   
        except Exception as e:
            self.logger.error("error: calc wind direction.  %s" %str(e))
        else:
            self.wind.xytext = (b_x, b_y)
            self.wind.xy = (h_x, h_y)

    def __update_az(self, az):

        try:
            new_x, new_y = self.__get_xy(degree=az, sign=-1, radius=0.125)
        except Exception as e:
            self.logger.error("error: calc subaru's direction.  %s" %str(e))
        else:
            #self.arrow.xy=(new_x, new_y)
            self.subaru._xy=(new_x, new_y)
            self.subaru.orientation = math.radians(180-az)
 
    def __update_el(self, el, state):

        color = self.normal_color 
        if state == "Pointing":
            pass
        elif (el >= self.alarm_high or el <= self.alarm_low):  
            color = self.alarm_color 
        elif (el >= self.warn_high or el <= self.warn_low):  
            color = self.warn_color

        try:
            Artist.remove(self.el)
            self.el = mpatches.Wedge((self.center, self.center), \
                                      theta1=180-el, \
                                      fc=color, ec=color, **self.el_kwargs) 
            self.axes.add_patch(self.el)
        except Exception as e:
            self.logger.error('error: updating. %s' %str(e))
            pass

    def update_azel(self, az, el, wind, state):
        ''' az = TSCS.AZ
            el = TSCS.EL 
            wind = TSCL.WINDD
            state = STATL.TELDRIVE '''

        self.logger.debug('updating az=%s el=%s state=%s'  %(str(az), str(el), state)) 
       
        self.__update_wind_direction(direction=wind)  
        self.__update_az(az)
        self.__update_el(el, state)
        
        self.draw()     

    def tick(self):
        ''' testing solo mode '''
        import random  
        random.seed()
        state=["Guiding(AG1)", "Guiding(AG2)", "Unknown", "##NODATA##",
               "##ERROR##", "Guiding(SV1)","Guiding(SV2)", "Guiding(AGPIR)",
               "Guiding(AGFMOS)", "Tracking", "Tracking(Non-Sidereal)", 
               "Slewing", "Pointing", "Guiding(HSCSCAG)", "Guiding(HSCSHAG)"]

        # el limit is between 0 and 90, 
        el = random.random()*random.randrange(0,150)
        indx = random.randrange(0,15)
        az = wind = random.random()*random.randrange(-360, 360)
        try:
            state=state[indx]
        except Exception:
            state='Pointing' 
        self.update_azel(az, el, wind, state)



def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('el', options)
 
    class AppWindow(QtGui.QMainWindow):
        def __init__(self):
            QtGui.QMainWindow.__init__(self)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=250; self.h=250;
            self.setup()

        def setup(self):
            self.resize(self.w, self.h)
            self.main_widget = QtGui.QWidget(self)

            l = QtGui.QVBoxLayout(self.main_widget)
            azel = AzEl(self.main_widget, logger=logger)
            l.addWidget(azel)

            timer = QtCore.QTimer(self)
            QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), azel.tick)
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
