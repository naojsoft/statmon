from __future__ import absolute_import
import PlBase
import EnvMon2
from qtpy import QtWidgets, QtCore


class EnvMon2Plugin(PlBase.Plugin):
    """ EnvMon """
    aliases = ['STATL.CSCT_WINDS_MAX']

    def build_gui(self, container):
        self.root = container

        qtwidget = QtWidgets.QWidget()

        self.em = EnvMon2.EnvMon(qtwidget, logger=self.logger)
       
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.em, stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.controller.register_select('envmon2', self.update, EnvMon2Plugin.aliases)
        self.em.start()

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        self.em.update_envmon(status_dict=statusDict)

