#
# T. Inagaki
#
from ginga.gw import Widgets

class Dummy(Widgets.Label):
    def __init__(self, parent=None, width=125, height=60, logger=None):
        super().__init__('')

        self.bg = 'white'

        self.resize(width, height)
        self.set_color(fg=self.bg, bg=self.bg)
