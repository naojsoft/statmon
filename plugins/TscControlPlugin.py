from ginga.gw import Widgets
import PlBase
import TscControl


class TscControlPlugin(PlBase.Plugin):
    """ TscControl """

    aliases = ['GEN2.TSCLOGINS', 'GEN2.TSCMODE']

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        self.tc = TscControl.TscControl(logger=self.logger)

        self.root.add_widget(Widgets.wrap(self.tc), stretch=1)

    def start(self):
        self.controller.register_select('tsccontrol', self.update,
                                        TscControlPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('TSCCONTROL status={}'.format(statusDict))
        self.tc.update_tsccontrol(**statusDict)
