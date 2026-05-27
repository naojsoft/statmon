#
# T. Inagaki
#
from ginga.gw import Widgets

from error import ERROR


class Label(Widgets.Label):
    ''' draw a label on a canvas  '''
    def __init__(self, parent=None, font='UnDotum', fs=27, weight='normal',
                 frame=False, linewidth=1, midlinewidth=2,
                 width=350, height=75, fg='green', bg='white',
                 align='center', fixsize=False, logger=None):
        super().__init__()

        self.warn = 'orange'
        self.alarm = 'red'
        self.normal = 'green'
        self.font = font
        self.fg = fg
        self.bg = bg
        self.width = width
        self.height = height
        self.logger = logger

        #fontweight = {'normal': QtGui.QFont.Normal, 'bold':QtGui.QFont.Bold}
        #self.font.setWeight(fontweight[weight])
        self.set_text('Initializing')
        align = {'center': 'center',
                 'left': 'left',
                 'right': 'right',
                 'vcenter': 'center'}[align]
        self.set_halign(align)
        self.set_font(self.font, int(fs))

        self.set_color(fg=self.fg, bg=self.bg)

        if fixsize:
            self.resize(self.width, self.height)

        if frame:
            #self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Raised)
            #self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
            #self.setLineWidth(int(linewidth))
            #elf.setMidLineWidth(midlinewidth)
            pass
