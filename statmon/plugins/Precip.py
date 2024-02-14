#!/usr/bin/env python

import os
import sys

from datetime import datetime
import time

from qtpy import QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.figure import SubplotParams
from matplotlib.artist import Artist

from g2base import ssdlog
import PlBase
from error import *
from CustomLabel import Label, QtWidgets, QtCore


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class PrecipCanvas(FigureCanvas):
    """ Dome Flat drawing canvas """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):

        sub = SubplotParams(left=0, bottom=0, right=1,
                            top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height),
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

        #FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w = 200
        self.h = 25
        #FigureCanvas.resize(self, self.w, self.h)

        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        w = 0.11
        h = 0.6
        label_y = 0.2
        frame_y = 0.1
        common_keys = dict(va='baseline', ha="center", size=13, color=self.normal)
        kwargs = dict(fc=self.bg, ec=self.normal, lw=1.5)

        # Wet Label
        self.axes.text(0.11, label_y, "Wet", common_keys)

        # Wet frame
        bs = mpatches.BoxStyle("Square", pad=0.05)
        self.frame_wet = mpatches.FancyBboxPatch((0.05, frame_y), w, h, \
                                          boxstyle=bs, **kwargs)
        self.axes.add_patch(self.frame_wet)

        # Dry Label
        self.axes.text(0.36, label_y, "Dry", common_keys)

        # Dry frame
        self.frame_dry = mpatches.FancyBboxPatch((0.3,frame_y), w, h, \
                                          boxstyle=bs, **kwargs)
        self.axes.add_patch(self.frame_dry)

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

    def set_wet(self, status, alpha):
        self.frame_wet.set_fc(status)
        self.frame_wet.set_alpha(alpha)

    def set_dry(self, status, alpha):
        self.frame_dry.set_fc(status)
        self.frame_dry.set_alpha(alpha)


class Precip(PrecipCanvas):
    """ Dome Flat Watt"""
    def __init__(self,*args, **kwargs):
        super(Precip, self).__init__(*args, **kwargs)

        self.stale_time = 600000  #  10 min in sec

    def update_precip(self, precip, precip_time):
        ''' precip  = GEN2.PRECIP.SENSOR1.STATUS
            precip_time = GEN2.PRECIP.SENSOR1.TIME
        '''
        self.logger.debug(f'updating precip={precip}, time={precip_time}')
        self._precip(precip, precip_time)
        self.draw()

    def _precip(self, precip, precip_time):

        time_diff = datetime.fromtimestamp(time.time()) - datetime.fromtimestamp(precip_time)
        self.logger.debug(f'precip time diff={time_diff.total_seconds()}')

        if precip in ERROR or (time_diff.total_seconds() > self.stale_time):
            self.logger.debug(f'no precip. {precip}')
            self.set_wet(status=self.warn, alpha=1)
            self.set_dry(status=self.warn, alpha=1)
        elif precip.upper() == "WET":
            self.logger.debug(f'precip is wet. {precip}')
            self.set_wet(status=self.alarm, alpha=1)
            self.set_dry(status=self.bg, alpha=1)
        elif precip.upper() == "DRY":
            self.logger.debug(f'precip is dry. {precip}')
            self.set_dry(status=self.normal, alpha=0.3)
            self.set_wet(status=self.bg, alpha=1)
        else:  # precip got weird value
            self.logger.debug(f'precip has weird value. {precip}')
            self.set_wet(status=self.alarm, alpha=1)
            self.set_dry(status=self.alarm, alpha=1)


class PrecipDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super(PrecipDisplay, self).__init__(parent)

        self.precip_label = Label(parent=parent, fs=13, width=175,
                                  height=25, align='vcenter',
                                  weight='normal', logger=logger)

        self.precip_label.setText('Precip Sensor1')
        self.precip_label.setIndent(15)


        self.precip = Precip(parent=parent, logger=logger)
        self._set_layout()

    def _set_layout(self):
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(0)
        hlayout.setContentsMargins(0, 0, 0, 0)

        hlayout.addWidget(self.precip_label)
        hlayout.addWidget(self.precip)
        self.setLayout(hlayout)

    def update_precip(self, precip, precip_time):
        self.precip.update_precip(precip, precip_time)

    def tick(self):
        ''' testing solo mode '''
        import random

        idx = random.randrange(0, 4)
        idx2 = random.randrange(0, 4)

        precip = ['WET', 'DRY', STATNONE, STATERROR]

        precip_time = [time.time(), 1707873823.5670083, 1707273823.5670083, 1706673823.5670083]

        try:
            precip = precip[idx]
            precip_time = precip_time[idx2]
        except Exception:
            pass
        else:
            self.update_precip(precip, precip_time)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('precip', options)

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
            dw = PrecipDisplay(self.main_widget, logger=logger)
            l.addWidget(dw)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(dw.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("Precip starting..."  ,5000)
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
        print('keyboard interruption')
        logger.info('keyboard interruption....')
        sys.exit(0)


if __name__ == '__main__':
    # Create the base frame for the widgets
    from argparse import ArgumentParser

    argprs = ArgumentParser(description="Precip status")

    argprs.add_argument("--debug", dest="debug", default=False,
                      action="store_true",
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
