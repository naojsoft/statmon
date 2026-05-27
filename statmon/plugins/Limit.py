#
# T. Inagaki
#
from CustomPlot import PlotWidget

from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
from matplotlib.lines import Line2D


class LimitCanvas(PlotWidget):
    """  Canvas to draw a limit """
    def __init__(self, parent=None, title='Limit', width=5, height=5,
                 alarm=[0,0], warn=[0,0], limit=[0,0], marker=0.0,
                 marker_txt='', logger=None):

        sub = SubplotParams(left=0.05,  right=0.95, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height),  facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.title = title
        self.limit_low = min(limit)
        self.limit_high = max(limit)
        self.alarm_low = min(alarm)
        self.alarm_high = max(alarm)
        self.warn_low = min(warn)
        self.warn_high = max(warn)
        self.marker = marker
        self.marker_txt = marker_txt

        self.cur_color = 'green'
        self.cmd_color = 'blue'
        self.warn_color = 'orange'
        self.alarm_color = 'red'

        # y axis values. these are fixed values.
        self.y_axis = [-1, 0.0,  1]
        self.center_y = 0.0
        self.init_x = 0.0  # initial value of x

        self.set_expanding(True, True)
        #FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w = 350
        self.h = 80
        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # position of current/cmd display
        self.y_curoffset = 0.35
        self.y_cmdoffset = -0.65

        # current,commanded text
        self.bbox = dict(boxstyle="round, pad=0.15",facecolor=self.cur_color, ec="none",  alpha=0.75,)
#        center_x='%.1f' %self.center_x
        self.cur_anno = self.axes.annotate(self.init_x,  fontsize=13, weight='bold',
                                         xy=(self.init_x, self.center_y),
                                         xytext=(self.init_x, self.y_curoffset),
                                         bbox=self.bbox, color='w',
                                         #rotation=-90,
                                         arrowprops=dict(arrowstyle="-|>", relpos=(0.5, -0.2)),
                                         transform=self.axes, horizontalalignment='center')

        self.cmd_anno = self.axes.annotate(self.init_x,  fontsize=12, weight='bold',
                                         xy=(self.init_x, self.center_y),
                                         xytext=(self.init_x, self.y_cmdoffset),
                                         bbox=dict(boxstyle="round,pad=0.15", facecolor=self.cmd_color,
                                                   ec="none",  alpha=0.05, ),
                                         color=self.cmd_color,
                                         arrowprops=dict(arrowstyle="-|>", relpos=(0.5, 0)),
                                         transform=self.axes, horizontalalignment='center')

        # draw x-axis
        line_kwargs = dict(alpha=0.7, ls='-', lw=1.5 , color=self.cur_color,
                         marker='|', ms=8.0, mew=1.5, markevery=(1,10))

        line_edge_kwargs = dict(alpha=0.9, ls='-', lw=2 , color=self.warn_color,
                                marker='|', ms=20.0, mew=3, markevery=(1,1), mec=self.alarm_color)

        middle = [self.warn_low,  self.marker, self.warn_high]
        line_middle = Line2D(middle, [self.center_y]*len(middle), **line_kwargs)

        right = [self.warn_high, self.limit_high]
        line_right = Line2D(right, [self.center_y]*len(right), **line_edge_kwargs)

        left = [self.warn_low, self.limit_low]
        line_left = Line2D(left, [self.center_y]*len(left), **line_edge_kwargs)

        self.axes.add_line(line_right)
        self.axes.add_line(line_left)
        self.axes.add_line(line_middle)

        # draw text
        self.axes.text(0, 0.9, self.title, color=self.cmd_color, va='baseline', ha='left', transform=self.axes.transAxes, fontsize=11)
        self.axes.text(0.5, 0.95, 'current',   va='baseline', ha='center',
                       transform=self.axes.transAxes, fontsize=11)
        self.axes.text(0.5, 0.1, 'commanded',  va='top', ha='center',
                       transform=self.axes.transAxes, fontsize=10)

        # draw labels of x-axis
        x_axis = [self.limit_low, self.marker, self.limit_high]
        x_label = [self.limit_low, self.marker_txt, self.limit_high]

        for (x, label) in zip(x_axis, x_label) :
            self.axes.text(x, -0.8,  '%s'%label, fontsize=11,  va='center', ha='center', alpha=0.7)
        # set x,y scale.   note: added +-0.00001 in order to display a value that exceeds possitive/negative limit, otherwise, a value will disappear only when this widget is plugged into telstat
        self.axes.set_xlim(self.limit_low-0.00001, self.limit_high+0.00001)
        self.axes.set_ylim(min(self.y_axis), max(self.y_axis))
        # # disable default x/y axis drawing
        #self.axes.set_xlabel(False)
        #self.axes.set_ylabel(False)
        self.axes.axison = False
        self.draw()


class Limit(LimitCanvas):
    """ AZ/EL/Rotator/Probe Limit  """
    def __init__(self,*args, **kwargs):

        LimitCanvas.__init__(self, *args, **kwargs)

    def get_val_state(self, val, state=None):

        color = self.cur_color
        try:
            text = '%.1f' %val
        except Exception as e:
            self.logger.error(f'error: value not number={val}.  {e}')
            text = 'No Data'
            color = self.alarm_color
            val = 0
        else:
            if val > self.limit_high:
                color = self.alarm_color
                val = self.limit_high
            elif val < self.limit_low:
                color = self.alarm_color
                val=self.limit_low
            elif (val >= self.alarm_high or val <= self.alarm_low):
                color = self.alarm_color
            elif (val >= self.warn_high or val <= self.warn_low):
                color = self.warn_color

        return (text, val, color)

    def update_limit(self, current , cmd, state=None):

        self.logger.debug('updating current={current}, cmd={cmd} ,state={state}')

        # ignore alarm/warning if el in pointing
        if state and state.strip() == 'Pointing':
            color = self.cur_color

        text, val, color = self.get_val_state(current, state)

        try:
            self.cur_anno.set_text(text)
            self.cur_anno.xy = (val, self.center_y)
            #self.cur_anno.xytext = (val, self.y_curoffset)
            self.cur_anno.set_x(val)
            #self.cur_anno.set_y(self.y_curoffset)
            self.bbox['facecolor'] = color
            self.cur_anno.set_bbox(self.bbox)
        except Exception as e:
            self.logger.error(f'error: setting current value. {e}')
            pass

        text, val, color = self.get_val_state(cmd)
        try:
            #self.cmd_anno.xytext=(val, self.y_cmdoffset)
            self.cmd_anno.set_text(text)
            self.cmd_anno.xy = (val, self.center_y)
            self.cmd_anno.set_x(val)
            #self.cmd_anno.set_y(self.y_cmdoffset)
        except Exception as e:
            self.logger.error(f'error: setting cmd value. {e}')
            pass

        self.draw()


class ElLimit(Limit):
    ''' EL Limit for testing '''
    def __init__(self,*args, **kwargs):
        super(ElLimit, self).__init__(*args, **kwargs)
