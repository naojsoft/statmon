#
# E. Jeschke
#

from matplotlib.figure import Figure

from ginga.gw.Plot import FigureCanvas, PlotWidget as GingaPlotWidget
from ginga.plot.PlotView import PlotViewEvent
from ginga.misc.Settings import SettingGroup


class PlotWidget(GingaPlotWidget):

    def __init__(self, figure=None, logger=None):

        settings = SettingGroup(name="customplot", logger=logger)
        if figure is None:
            figure = Figure()
        plot = PlotViewEvent(logger=logger, settings=settings,
                             figure=figure, addaxis=False)
        # assigns to self.plot
        super().__init__(plot)

        #self.set_expanding(False, False)

    def draw(self):
        self.plot.redraw()
