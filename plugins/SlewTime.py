from datetime import timedelta
from qtpy import QtWidgets, QtCore, QtGui

import PlBase


class SlewTime(PlBase.Plugin):
    """ Show the remaining slew time. """
    aliases = ['STATS.SLEWING_TIME', 'STATS.SLEWING_STATUS']

    def build_gui(self, container):
        self.lbl = QtWidgets.QLabel()
        self.lbl.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl.setStyleSheet("QLabel {color :green ; background-color:white }")
        fontfamily = "Sans"
        self.smfont = QtGui.QFont(fontfamily, 12, QtGui.QFont.Normal)
        self.lbl.setFont(self.smfont)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.lbl, stretch=1)
        container.setLayout(layout)

    def start(self):
        self.controller.register_select(str(self), self.update, self.aliases)

    def update(self, statusDict):
        self.logger.info('status=%s' % str(statusDict))
        if statusDict['STATS.SLEWING_STATUS'] == 'NO':
            self.lbl.setText("Slew Time: (Not Slewing)")
            return

        time_sec = statusDict['STATS.SLEWING_TIME']
        if isinstance(time_sec, float):
            mn, sec = divmod(time_sec, 60)
            hr, mn = divmod(mn, 60)
            hr, mn, sec = int(hr), int(mn), int(sec)
            self.lbl.setText(f"Slew Time: {hr:02d}:{mn:02d}:{sec:02d}")
        else:
            self.lbl.setText(f"Slew Time: ERROR")
            

    def __str__(self):
        return 'slewtime'
