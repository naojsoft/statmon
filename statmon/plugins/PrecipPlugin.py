from ginga.gw import Widgets
from qtpy import QtWidgets, QtCore

import PlBase
import Precip


class PrecipPlugin(PlBase.Plugin):
    """ Precip """
    aliases = ['GEN2.PRECIP.SENSOR1.STATUS', 'GEN2.PRECIP.SENSOR1.TIME']

    def build_gui(self, container):
        self.root = container

        qtwidget = QtWidgets.QWidget()

        self.precip = Precip.PrecipDisplay(qtwidget, logger=self.logger)

        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)
        self.root.add_widget(Widgets.wrap(self.precip), stretch=0)

    def start(self):
        self.controller.register_select('precip', self.update,
                                        PrecipPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            precip = statusDict.get(PrecipPlugin.aliases[0])
            precip_time = statusDict.get(PrecipPlugin.aliases[1])
            self.precip.update_precip(precip, precip_time)
        except Exception as e:
            self.logger.error(f'error: updating status. {e}')
