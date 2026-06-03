#
# T. Inagaki
#
from CustomPlot import PlotWidget

from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
import matplotlib.patches as mpatches


class CellCanvas(PlotWidget):
    """ AG/SV/FMOS/AO188 Plotting """
    def __init__(self, parent=None, width=3, height=3,  logger=None):

        sub = SubplotParams(left=0.0, right=1, bottom=0, top=1,
                            wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.closed_color = 'black'
        self.open_color = 'white'
        self.onway_color = 'orange'
        self.alarm_color = 'red'

        # width/hight of widget
        self.w = 250
        self.h = 30
        self.set_expanding(True, False)
        self.set_min_size(self.w, self.h)
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

        self.axes.axison = False
        self.draw()


class CellCover(CellCanvas):

    """A canvas that updates itself every second with a new plot."""
    def __init__(self,*args, **kwargs):
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
