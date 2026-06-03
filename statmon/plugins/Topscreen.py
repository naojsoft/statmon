#
# T. Inagaki
#
import math
import numpy as np

from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

from error import ERROR
from g2cam.status.common import STATNONE, STATERROR

import PlBase
from CustomPlot import PlotWidget


class TopscreenCanvas(PlotWidget):
    """ Topscreen """
    def __init__(self, parent=None, width=1, height=1,  logger=None):

        sub = SubplotParams(left=0, bottom=0, right=1,
                            top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        # y axis values. these are fixed values.
        self.y_axis = [-1.0, 0, 1]
        self.center_y = 0.0

        # FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Fixed, \
        #                            QtWidgets.QSizePolicy.Fixed)
        # FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w = 500
        self.h = 50
        self.set_expanding(True, False)
        self.set_min_size(self.w, self.h)

        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        limit = [30.3, 0] # there is a case of tscl.tsfpos=24.28, so limit is at least 24.28 + 6 = 30.28
        front_init = 16
        self.rear1_pos=rear1_init = 4
        rear2_init = 10

        # top screen front/rear length/width
        self.screen_len = 6 # 6 meter
        screen_width = 0.2

        self.screen_color = 'green'
        self.normal_color = 'black'
        self.alarm_color = 'red'

        # front/rear top screen
        ts_kwargs = dict(alpha=0.8, fc=self.screen_color,
                         ec=self.screen_color, lw=1, )
        self.front = mpatches.Rectangle((front_init, screen_width - screen_width),
                                        self.screen_len, screen_width, **ts_kwargs)

        self.rear1 = mpatches.Rectangle((rear1_init, screen_width * 2),
                                        self.screen_len, screen_width,
                                        **ts_kwargs)
        self.rear2 = mpatches.Rectangle((rear2_init, screen_width),
                                        self.screen_len, screen_width,
                                        **ts_kwargs)

        self.axes.add_patch(self.front)
        self.axes.add_patch(self.rear1)
        self.axes.add_patch(self.rear2)

        # draw x-axis line
        line_kwargs = dict(alpha=0.7, ls='-', lw=0.7 , color=self.screen_color,
                           marker='|', ms=10.0, mew=2, markevery=(0,1))

        offset_drawing = 0.04
        middle = [max(limit) - offset_drawing, min(limit) + offset_drawing]
        line = Line2D(middle, [self.center_y] * len(middle), **line_kwargs)
        self.axes.add_line(line)

        # draw text
        self.text = self.axes.text(0.5, 0.2, 'Initializing',
                                   va='baseline', ha='center',
                                   transform = self.axes.transAxes,
                                   color=self.normal_color,
                                   fontsize=13)

        # set x,y limit values
        self.axes.set_xlim(max(limit), min(limit))
        self.axes.set_ylim(min(self.y_axis), max(self.y_axis))
        # disable default x/y axis drawing
        #self.axes.set_xlabel(False)
        #self.axes.apply_aspect()
        self.axes.set_axis_off()

        #self.axes.set_xscale(10)
        self.axes.axison = False
        #self.draw()


class Topscreen(TopscreenCanvas):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):

        TopscreenCanvas.__init__(self, *args, **kwargs)
        #super().__init__(*args, **kwargs)

    def update_topscreen(self, mode, front , rear):
        ''' mode = TSCV.TopScreen
            front = TSCL.TSFPOS
            rear = TSCL.TSRPOS
        '''
        free = 0x10
        link = 0x0C
        color = self.normal_color

        self.logger.debug(f'mode={mode}')

        if mode in ERROR:
            mode = 'Top Screen Undefined'
            color = self.alarm_color
        elif mode & free:
            mode = 'Top Screen Free'
        elif mode & link:
            mode = 'Top Screen Link'
        else:
            mode = 'Top Screen Mode Undef'
            color = self.alarm_color

        self.text.set_text(mode)
        self.text.set_color(color)

        self.logger.debug(f'updating pre_rear1={self.rear1_pos}')

        try:
            if rear < self.rear1_pos:
                self.rear1_pos = rear
            elif ((self.rear1_pos+self.screen_len) < rear):
                self.rear1_pos = rear-self.screen_len
            self.logger.debug(f'updating front={front}, rear1={self.rear1_pos}, rear2={rear}')

            self.front.set_x(front)
            self.rear1.set_x(self.rear1_pos)
            self.rear2.set_x(rear)

        except Exception as e:
            self.logger.error(f'error: front={front}, rear={rear}. {e}')

        self.draw()
