#!/usr/bin/env python

import os
import sys
import math
import numpy as np

from qtpy import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.figure import SubplotParams

from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR
import PlBase
from error import *

progname = os.path.basename(sys.argv[0])


class WindscreenCanvas(FigureCanvas):
    """ Windscreen """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):

#        sub  =SubplotParams(left=0, bottom=0.234, right=1, \
#                            top=0.998, wspace=0, hspace=0)

        sub = SubplotParams(left=0, bottom=0.03, right=1, \
                            top=1, wspace=0, hspace=0)

        self.fig = Figure(figsize=(width, height), facecolor='white', \
                          subplotpars=sub)

        #self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        #self.fig = Figure(facecolor='white')
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        #self.axes.grid(True)

        self.limit = [-14.5, 14.5]

        self.wind = 'blue'
        self.normal = 'green'
        self.warn = 'orange'
        self.alarm = 'red'

        # y axis values. these are fixed values.
        self.x_axis = [0, 1]
        self.y_axis = [-14.5, 14.5]
        self.center_x = 0.5
        self.init_x = 0.0  # initial value of x

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        #FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # width/hight of widget
        self.w = 125
        self.h = 450
        #FigureCanvas.resize(self, self.w, self.h)

        # top screen lenght/width
        self.ts_len = 6
        self.ts_width = 0.1

        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # position of current/cmd display
        self.y_curoffset = 0.35
        self.y_cmdoffset = -0.65


        #self.axes.add_patch(self.rear)
        # draw x-axis
        line_kwargs = dict(alpha=0.7, ls='-', lw=1 , color=self.normal,
                         marker='_', ms=15.0, mew=1.0, markevery=(0,1))
#        line_kwargs=dict(alpha=0.7, ls='-', lw=1 , color=self.normal,
#
#                         marker='v', ms=17.0, mew=0.5, markevery=(1,2))


        middle = [min(self.limit),  max(self.limit)]
        line = Line2D([0.87]*len(middle), [0, 14.5],  \
                      #transform=self.axes.transAxes, \
                      **line_kwargs)
        self.axes.add_line(line)



        line_kwargs = dict(alpha=0.7, ls=':', lw=5, color=self.normal,
                         marker='', ms=7.0, mew=1.0, markevery=(1,2))



        y = math.tan(math.radians(90)) * 14.5
        self.light = Line2D([2.0, 0], [0, y],  \
                      #transform=self.axes.transAxes, \
                      **line_kwargs)
        self.axes.add_line(self.light)




        ts_kwargs = dict(alpha=0.7, fc=self.wind, ec=self.wind, lw=1.5)

        self.windscreen = mpatches.Rectangle((self.center_x-(self.ts_width/2.0)+0.425, 0.0), \
                                           self.ts_width, 0, \
                                           **ts_kwargs)

        self.axes.add_patch(self.windscreen)

        # draw text
        self.msg = self.axes.text(0.9, 0.48, 'Init', \
                                  color=self.normal,  va='top', ha='right', \
                                  transform=self.axes.transAxes, fontsize=13)

        # set x,y limit values
        self.axes.set_ylim(min(self.limit),  max(self.limit))
        self.axes.set_xlim(min(self.x_axis), max(self.x_axis))
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


class Windscreen(WindscreenCanvas):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):

        #super(AGPlot, self).__init__(*args, **kwargs)
        WindscreenCanvas.__init__(self, *args, **kwargs)

    def __msg(self,  drv, windscreen, cmd, pos):

        color = self.normal

        if windscreen == 0x02: # windscreen free
            msg = 'Windscreen\nFree'
        elif windscreen == 0x01: # windscreen link
            msg = 'Windscreen\nLink'
        else:# windscreen undefined
            msg = 'WindScreen\nMode Undef'
            color = self.alarm

        if pos in ERROR:
            color = self.alarm
            msg += '\nNo Pos Data'
        elif cmd in ERROR:
            color = self.alarm
            msg += '\nNo Cmd Data'
        elif not drv == 0x04 and pos <= 5.0: # drive not on
            pass #msg+='\n'
        elif not drv == 0x04 and pos > 5.0: # drive not on
            color=self.alarm
            msg += '\nDrvOff/PosHigh'
        elif  drv == 0x04 and windscreen == 0x02:# drive on and Free
            color = self.alarm
            msg += '\nDriveOn'
        # drive on/link/cmd==pos
        elif drv == 0x04 and windscreen == 0x01 and math.fabs(cmd-pos) <= 1.0:
            pass #msg+='\n'   # GREEN, no alerts
        # drive on/link/ cmd!=pos
        elif  drv == 0x04 and windscreen == 0x01 and (cmd-pos > 1.0):
            color = self.warn
            msg += '\nPos!=Cmd'
        #drive on/link/ cmd-pos < -1
        elif  drv == 0x04 and windscreen == 0x01:
            color = self.alarm
            msg += '\nWS OBSTRUCT'
        else:
            #color=self.warn
            pass
            #msg+='\n'
        return (msg, color)

    def __update_lightpath(self, el):

        try:
            y = math.tan(math.radians(el)) * 14.5
        except Exception:
            pass
        else:
            if 0 < el < 35:
                offset = 0.055 + (el-10) * 0.04
            elif 35 <= el < 50:
                offset = 1.1 + (el-35) * 0.06
            elif 50 <= el:
                offset = 2.15 + (el-50) * 0.12
            else:
                offset = 0

            # 10 0.1, 15 0.3, 20 0.5, 25 0.7, 30 0.9,
            # 35 1.1, 40 1.4, 45 1.7, 50 2.0,   55 2.6, 60 3.2
            self.light.set_ydata([0, y+offset])

    def update_windscreen(self, drv, windscreen, cmd, pos, el):
        ''' drv = TSCV.WINDSDRV
            windscreen = TSCV.WindScreen
            pos = TSCL.WINDSPOS
            cmd = TSCL.WINDSCMD
            el = TSCS.EL
        '''

        self.logger.debug(f'updating drv={drv}, ws={windscreen}, cmd={cmd}, pos={pos}')

        msg, color=self.__msg(drv, windscreen, cmd, pos)

        self.msg.set_text(msg)
        #self.msg.set_backgroundcolor(color)
        self.msg.set_color(color)

        self.windscreen.set_color(color)
        if not pos in ERROR:
            self.windscreen.set_height(pos)

        self.__update_lightpath(el)

        self.draw()

    def tick(self, el=None):
        ''' testing  mode solo '''
        import random
        random.seed()

        drv = [0x08, "Unknown",  None, 0x04, STATNONE, STATERROR]
        windscreen = ["Unknown", 0x01,  None, STATNONE, 0x02,
                      STATERROR]

        indx = random.randrange(0, 6)
        #  0 ~ 14.9m
        pos = random.random()*random.randrange(0, 16)
        cmd = random.random()*random.randrange(0, 16)

        if el is None:
            el = random.random()*random.randrange(0,100)

        drv = drv[indx]
        windscreen = windscreen[indx]

        self.update_windscreen(drv, windscreen, cmd, pos, el)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('windscreen', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            QtWidgets.QMainWindow.__init__(self)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w = 125; self.h = 500;
            self.setup()

        def setup(self):
            self.resize(self.w, self.h)
            self.main_widget = QtWidgets.QWidget(self)

            l = QtWidgets.QVBoxLayout(self.main_widget)
            windscreen = Windscreen(self.main_widget, logger=logger)

            l.addWidget(windscreen)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(windscreen.tick)
            timer.start(options.interval)
            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("windscreen starting..."  ,5000)
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
        print('keyboard interruption...')
        logger.info('keyboard interruption....')
        sys.exit(0)


if __name__ == '__main__':
    # Create the base frame for the widgets
    from argparse import ArgumentParser

    argprs = ArgumentParser(description="Windsc status")

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
