#
# CalPlugin.py -- calibration lamps plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
import math

from ginga.gw import Widgets
from ginga.misc import Bunch

import PlBase

clr_status = dict(off='white', normal='black', warning='orange', alarm='red')

aliases = ['GEN2.TSCLOGINS', 'GEN2.TSCMODE']


class TscControlPlugin(PlBase.Plugin):
    """ TscControl """

    def build_gui(self, container):

        self.w = Bunch.Bunch()

        gbox = Widgets.GridBox(rows=1, columns=4)
        gbox.set_border_width(2)
        gbox.set_row_spacing(4)
        gbox.add_widget(Widgets.Label("TSC Login:"), 0, 0)
        self.w.tsc_login = Widgets.Label("", halign='center')
        gbox.add_widget(self.w.tsc_login, 0, 1)
        gbox.add_widget(Widgets.Label("TSC Priority:"), 0, 2)
        self.w.tsc_mode = Widgets.Label("", halign='center')
        gbox.add_widget(self.w.tsc_mode, 0, 3)

        container.add_widget(gbox, stretch=0)

    def start(self):
        self.controller.register_select('tsccontrol', self.update, aliases)

    def update(self, status_dct):
        self.logger.debug('status={}'.format(str(status_dct)))
        self.update_tscstatus(status_dct)

    def update_tscstatus(self, status_dct):

        tsclogin = status_dct['GEN2.TSCLOGINS']
        #tsclogin = tsclogin.replace('%', '')
        self.logger.debug(f'tsc login. {tsclogin}')

        try:
            assert "OCS" in tsclogin
            text = 'Logged IN({0})'.format(tsclogin)
            color = clr_status['normal']
        except Exception as e:
            text = 'Logged OUT'
            color = clr_status['alarm']
            self.logger.warning(f'warning: gen2 logged out. tsclogin={tsclogin}')

        self.w.tsc_login.set_text(text)
        self.w.tsc_login.set_color(fg=color)

        tscmode = status_dct['GEN2.TSCMODE']
        if not tscmode:
            text = 'None'
            color = clr_status['alarm']
        elif "OBS" in  tscmode:
            text = '{0}'.format(tscmode)
            color = clr_status['normal']
        else:
            text = '{0}'.format(tscmode)
            color = clr_status['alarm']
        self.logger.debug(f'tsc mode. {tscmode}')

        self.w.tsc_mode.set_text(text)
        self.w.tsc_mode.set_color(fg=color)
