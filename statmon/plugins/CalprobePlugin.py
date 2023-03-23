import PlBase
import Calprobe
from ginga.gw import Widgets

class CalprobePlugin(PlBase.Plugin):
    """ Cal Source Probe Plugin """
    aliases=['TSCL.CAL_POS']

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        self.calprobe = Calprobe.CalProbeDisplay(logger=self.logger)

        self.root.add_widget(Widgets.wrap(self.calprobe), stretch=1)

    def start(self):
        self.controller.register_select('calprobe', self.update,
                                        CalprobePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            probe = statusDict.get(CalprobePlugin.aliases[0])

            self.calprobe.update_calprobe(probe=probe)
        except Exception as e:
            self.logger.error('error: updating status. %s' %str(e))
