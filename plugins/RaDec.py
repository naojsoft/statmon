#
# RaDec.py -- RA/DEC plugin for StatMon
# 
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Thu Apr  5 14:21:18 HST 2012
#]
#
import PlBase

from PyQt4 import QtGui, QtCore

labels = (('ra', 'FITS.SBR.RA'), ('dec', 'FITS.SBR.DEC'),
          ('az', 'FITS.SBR.AZIMUTH'), ('el', 'FITS.SBR.ALTITUDE'),
          ('rot', 'FITS.SBR.INSROT'),
          )

class RaDec(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        container.setLayout(layout)
        
        self.msgFont = QtGui.QFont("Fixed", 24)

        self.w = {}
        for name, alias in labels:
            w = QtGui.QLabel(name)
            w.setFont(self.msgFont)
            layout.addWidget(w, stretch=0)
            self.w[name] = w

    def start(self):
        aliases = map(lambda t: t[1], labels)
        self.controller.register_select('radec', self.update, aliases)

    def update(self, statusDict):
        for name, alias in labels:
            w = self.w[name]
            w.setText(str(statusDict[alias]))
        
    
    def __str__(self):
        return 'radec'
    
#END
