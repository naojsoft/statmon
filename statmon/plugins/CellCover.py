#!/usr/bin/env python

import os
import sys
import math
import numpy as np

from qtpy import QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR
import PlBase
from error import ERROR

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class CellCanvas(FigureCanvas):
    """ AG/SV/FMOS/AO188 Plotting """
    def __init__(self, parent=None, width=3, height=3,  logger=None):

        sub=SubplotParams(left=0.0, right=1, bottom=0, top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white', subplotpars=sub )
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        #self.axes.grid(True)

        self.closed_color = 'black'
        self.open_color = 'white'
        self.onway_color = 'orange'
        self.alarm_color = 'red'

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, \
        #                            QtWidgets.QSizePolicy.Expanding)
        # FigureCanvas.updateGeometry(self)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Fixed, \
                                   QtWidgets.QSizePolicy.Fixed)

        # width/hight of widget
        self.w = 250
        self.h = 30
        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # draw cell cover
        cell_kwargs = dict(alpha=0.7, fc=self.closed_color, ec='grey', lw=1.5)
        self.cell= mpatches.Rectangle((0.25, 0.75), 0.5, 0.2, **cell_kwargs)
        self.axes.add_patch(self.cell)

        # draw text
        self.text = self.axes.text(0.5, 0.5, 'Initializing', \
                                 va='top', ha='center', \
                                 transform=self.axes.transAxes, fontsize=11)

        self.axes.axison=False
        self.draw()

    def minimumSizeHint(self):
        return QtCore.QSize(self.w, self.h)

    def sizeHint(self):
         return QtCore.QSize(self.w, self.h)


class CellCover(CellCanvas):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):

        #super(AGPlot, self).__init__(*args, **kwargs)
        CellCanvas.__init__(self, *args, **kwargs)

    def update_cell(self, cell):
        ''' cell = 'TSCV.CellCover'  '''
        self.logger.debug(f'updating cell={cell}')

        if cell == 0x01: # cell cover open
            self.text.set_text('Cell Cover Open')
            self.cell.set_facecolor(self.open_color)
        elif cell == 0x04: # cell cover close
            self.text.set_text('Cell Cover Closed')
            self.cell.set_facecolor(self.closed_color)
        elif cell == 0x00: # cell cover on-way
            self.text.set_text('Cell Cover OnWay')
            self.cell.set_facecolor(self.onway_color)
        else:  # # cell cover unknown status
            self.text.set_text('Cell Cover Undef')
            self.cell.set_facecolor(self.alarm_color)

        self.draw()

    def tick(self):
        ''' testing  mode solo '''
        import random
        random.seed()

        indx = random.randrange(0, 8)
        cell = [0x01, 'Unknown', None, 0x00, STATNONE, STATERROR, 0x04]
        try:
            cell = cell[indx]
        except Exception:
            cell = None

        self.update_cell(cell)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('cellcover', options)

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
            cell =  CellCover(self.main_widget, logger=logger)

            l.addWidget(cell)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(cell.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)

            self.statusBar().showMessage("Cellcover starting..." , 5000)
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

    from argparse import ArgumentParser

    argprs = ArgumentParser(description="CellCover status")


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
