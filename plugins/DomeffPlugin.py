import PlBase
import Domeff
from ginga.gw import Widgets


class DomeffPlugin(PlBase.Plugin):
    """ Domeff """
    aliases=['TSCV.DomeFF_A', 'TSCV.DomeFF_1B', 'TSCV.DomeFF_2B', \
             'TSCV.DomeFF_3B', 'TSCV.DomeFF_4B', \
             'TSCL.DOMEFF_A_VOL', \
             'TSCL.DOMEFF_1B_VOL', 'TSCL.DOMEFF_2B_VOL', \
             'TSCL.DOMEFF_3B_VOL', 'TSCL.DOMEFF_4B_VOL']

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        self.domeff=Domeff.DomeffDisplay(logger=self.logger)

        self.root.add_widget(Widgets.wrap(self.domeff), stretch=1)

    def start(self):
        self.controller.register_select('domeff', self.update,
                                        DomeffPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            ff_a = statusDict.get(DomeffPlugin.aliases[0])
            ff_1b = statusDict.get(DomeffPlugin.aliases[1])
            ff_2b = statusDict.get(DomeffPlugin.aliases[2])
            ff_3b = statusDict.get(DomeffPlugin.aliases[3])
            ff_4b = statusDict.get(DomeffPlugin.aliases[4])
            ff_a_v = statusDict.get(DomeffPlugin.aliases[5])
            ff_1b_v = statusDict.get(DomeffPlugin.aliases[6])
            ff_2b_v = statusDict.get(DomeffPlugin.aliases[7])
            ff_3b_v = statusDict.get(DomeffPlugin.aliases[8])
            ff_4b_v = statusDict.get(DomeffPlugin.aliases[9])



            self.domeff.update_domeff(ff_a=ff_a, ff_1b=ff_1b, ff_2b=ff_2b,
                                      ff_3b=ff_3b, ff_4b=ff_4b,
                                      ff_a_v=ff_a_v, ff_1b_v=ff_1b_v, ff_2b_v=ff_2b_v,
                                      ff_3b_v=ff_3b_v, ff_4b_v=ff_4b_v)
        except Exception as e:
            self.logger.error('error: updating status. %s' %str(e))
