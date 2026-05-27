#
# E. Jeschke
#

from matplotlib.figure import Figure

from ginga.gw.Widgets import WidgetBase
from ginga.gw.Plot import FigureCanvas


class PlotWidget(WidgetBase):

    def __init__(self, figure=None):
        WidgetBase.__init__(self)

        if figure is None:
            figure = Figure()
        self.figure = figure
        self.widget = FigureCanvas(figure)

    def get_widget(self):
        return self.widget

    def set_figure(self, figure):
        self.figure = figure
        figure.set_canvas(self.get_widget())

    def draw(self):
        self.figure.canvas.draw()
