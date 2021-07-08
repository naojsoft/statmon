import PlBase
import Precip
from qtpy import QtWidgets, QtCore


class PrecipPlugin(PlBase.Plugin):
    """ Precip """
    aliases = ['GEN2.PRECIP.SENSOR1.STATUS']

    def build_gui(self, container):
        self.root = container

        qtwidget = QtWidgets.QWidget()

        self.precip = Precip.PrecipDisplay(qtwidget, logger=self.logger)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.precip, stretch=1)
        container.setLayout(layout)

    def start(self):
        self.controller.register_select('precip', self.update,
                                        PrecipPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            precip = statusDict.get(PrecipPlugin.aliases[0])
            self.precip.update_precip(precip)
        except Exception as e:
            self.logger.error(f'error: updating status. {e}')
