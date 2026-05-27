#
# T. Inagaki
#
from CustomPlot import PlotWidget

from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
import matplotlib.patches as mpatches

from error import ERROR


class M1Canvas(PlotWidget):
    """ M1 Mirror """
    def __init__(self, parent=None, width=3, height=3, logger=None):

        sub = SubplotParams(left=0.0, right=1, bottom=0, top=1, wspace=0,
                            hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.closed_color = 'black'
        self.open_color = 'white'
        self.onway_color = 'orange'
        self.alarm_color = 'red'

        self.set_expanding(True, True)
        # FigureCanvas.updateGeometry(self)

        # width/hight of widget
        self.w = 250
        self.h = 70
        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # draw mirror
        m1_kwargs = dict(alpha=0.7, fc=self.closed_color, ec='grey', lw=2)
        self.m1 = mpatches.Wedge((0.5, 0.4), 0.495, 180, 360, **m1_kwargs)
        self.axes.add_patch(self.m1)

        # draw text
        self.text = self.axes.text(0.5, 0.5, 'Initializing', va='baseline', \
                                 ha='center', \
                                 transform=self.axes.transAxes, fontsize=13)

        self.axes.axison=False
        self.draw()


class M1Cover(M1Canvas):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):

        M1Canvas.__init__(self, *args, **kwargs)

    def update_m1cover(self, m1cover, m1cover_onway):
        ''' m1cover = TSCV.M1Cover
            m1cover_onway = TSCV.M1CoverOnway '''

        self.logger.debug(f'updating m1cover={m1cover}, m1cover_type={type(m1cover)}, m1_onway={m1cover_onway}')

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
            self.logger.error(f'Error: M1 cover. {e}')

        self.draw()
