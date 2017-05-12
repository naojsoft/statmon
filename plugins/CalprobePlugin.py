from __future__ import absolute_import
import PlBase
import Calprobe
from qtpy import QtWidgets, QtCore

class CalprobePlugin(PlBase.Plugin):
    """ Cal Source Probe Plugin """
    aliases=['TSCL.CAL_POS']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtWidgets.QWidget()

        self.calprobe = Calprobe.CalProbeDisplay(qtwidget, logger=self.logger)
       
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.calprobe, stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.controller.register_select('calprobe', self.update, \
                                         CalprobePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            probe = statusDict.get(CalprobePlugin.aliases[0])

            self.calprobe.update_calprobe(probe=probe)
        except Exception as e:
            self.logger.error('error: updating status. %s' %str(e))
            
