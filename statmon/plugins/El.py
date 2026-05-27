#
# T. Inagaki
#
from CustomPlot import PlotWidget

from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.figure import SubplotParams
from matplotlib.artist import Artist


class ElCanvas(PlotWidget):
    """ Elevation """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):

        sub = SubplotParams(left=0.0, bottom=0, right=0.999,
                            top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height),
                          facecolor='white', subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.limit_low = 0.0
        self.limit_high = 90.0;

        self.alarm_high = 89.5
        self.alarm_low = 10.0

        self.warn_high = 89.0
        self.warn_low = 15.0


        self.normal_color = 'green'
        self.warn_color = 'orange'
        self.alarm_color = 'red'

        # y axis values. these are fixed values.
        self.x_scale = [-0.001, 1.0]
        self.y_scale = [0.0,  1.0055]

        # width/hight of widget
        self.w = 250
        self.h = 250

        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # draw el frame
        el_kwargs = dict(alpha=0.6, fc='white', ec='black', lw=1.5)
        el = mpatches.Wedge((1,0), 1, 90, 180, **el_kwargs)
        self.axes.add_patch(el)

        # draw el angle
        el_kwargs = dict(alpha=0.5, fc=self.normal_color, \
                         ec=self.normal_color, lw=8)
        self.el = mpatches.Wedge((1,0), 0.99, 90, 180, **el_kwargs)
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


class El(ElCanvas):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):

        ElCanvas.__init__(self, *args, **kwargs)

    def __get_val_state(self, el, state):

        color = self.normal_color
        if state == "Pointing":
            return (el, color)

        if el > self.limit_high:
            color = self.alarm_color
            el=self.limit_high
        elif el < self.limit_low:
            color = self.alarm_color
            el = self.limit_low
        elif (el >= self.alarm_high or el <= self.alarm_low):
            color = self.alarm_color
        elif (el >= self.warn_high or el <= self.warn_low):
            color = self.warn_color

        return (el, color)

    def update_el(self, el, state):
        ''' el = TSCS.EL
            state = STATL.TELDRIVE '''

        self.logger.debug(f'updating el={el} state={state}')

        val,color = self.__get_val_state(el, state)

        try:
            Artist.remove(self.el)
            el_kwargs = dict(alpha=0.5, fc=color, ec=color, lw=8)
            self.el = mpatches.Wedge((1,0), 0.99, 180-val, 180, **el_kwargs)
            self.axes.add_patch(self.el)
            self.draw()
        except Exception as e:
            self.logger.error('error: updating. {e}')
            pass
