from __future__ import absolute_import
import sip
from qtpy import QtWidgets, QtCore

import PlBase
import TscControl


class TscControlPlugin(PlBase.Plugin):
    """ TscControl """

    aliases = ['GEN2.TSCLOGINS', 'GEN2.TSCMODE']

    def build_gui(self, container):
        self.root = container

        qtwidget = QtWidgets.QWidget()
        self.tc = TscControl.TscControl(qtwidget, logger=self.logger)
       
        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)
        self.vlayout.addWidget(self.tc,stretch=1)
        container.setLayout(self.vlayout)

    def start(self):
        self.controller.register_select('tsccontrol', self.update, TscControlPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('TSCCONTROL status={}'.format(statusDict))
        self.tc.update_tsccontrol(**statusDict) 
