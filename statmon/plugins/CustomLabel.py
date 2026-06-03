#
# T. Inagaki
#
from ginga.gw import Widgets, GwHelp

from error import ERROR


class Label(Widgets.Label):
    ''' draw a label on a canvas  '''
    def __init__(self, parent=None, font='sans', fs=27, weight='normal',
                 frame=False, linewidth=1, midlinewidth=2,
                 width=350, height=75, fg='darkgreen', bg='white',
                 align='center', fixsize=False, logger=None):
        super().__init__()

        self.warn = 'orange'
        self.alarm = 'red'
        self.normal = 'darkgreen'
        self.fg = fg
        self.bg = bg
        self.width = width
        self.height = height
        self.logger = logger

        font_spec = f'{font};normal;{weight}'
        self.font = GwHelp.get_font(font_spec, int(fs))
        self.set_text('Initializing')
        halign, valign = {'center': ['center', None],
                          'left': ['left', 'center'],
                          'right': ['right', 'center'],
                          'vcenter': [None, 'center']}[align]
        if halign is not None:
            self.set_halign(halign)
        if valign is not None:
            self.set_valign(valign)
        self.set_font(self.font)

        self.set_color(fg=self.fg, bg=self.bg)

        if fixsize:
            #self.resize(self.width, self.height)
            self.set_min_size(self.width, self.height)
            self.set_max_size(self.width, self.height)

        if frame:
            #self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Raised)
            #self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
            #self.setLineWidth(int(linewidth))
            #elf.setMidLineWidth(midlinewidth)
            pass
