#
# DomeffPlugin.py -- dome flats plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
import time

from ginga.gw import Widgets
from ginga.misc import Bunch
from ginga import colors

from g2cam.status.common import STATNONE, STATERROR
ERROR = ["Unknown", None, STATNONE, STATERROR, 'None']

import PlBase


clr_status = dict(off='white', normal='green', warning='orange', alarm='red')

aliases = dict(precip='GEN2.PRECIP.SENSOR1.STATUS',
               precip_time='GEN2.PRECIP.SENSOR1.TIME')

# How long if we haven't heard from the precipitation sensor that we
# consider it stale
stale_time_sec = 60


class PrecipPlugin(PlBase.Plugin):
    """ Precip """

    def build_gui(self, container):
        self.w = Bunch.Bunch()

        gbox = Widgets.GridBox(rows=1, columns=5)
        gbox.set_border_width(2)
        gbox.add_widget(Widgets.Label("Precip:"), 0, 0)
        gbox.add_widget(Widgets.Label(""), 0, 1)  # add spacer
        self.w.lamp_wet = Widgets.Label("Wet", halign='center')
        gbox.add_widget(self.w.lamp_wet, 0, 2)
        self.set_lamp(self.w.lamp_wet, clr_status['off'], 1.0)
        self.w.lamp_dry = Widgets.Label("Dry", halign='center')
        gbox.add_widget(self.w.lamp_dry, 0, 3)
        self.set_lamp(self.w.lamp_dry, clr_status['off'], 1.0)
        gbox.add_widget(Widgets.Label(""), 0, 4)  # add spacer

        container.add_widget(gbox, stretch=0)

    def start(self):
        self.controller.register_select('precip', self.update,
                                        list(aliases.values()))

    def update(self, status_dct):
        self.logger.debug('status=%s' % str(status_dct))
        try:
            self.update_precip(status_dct)

        except Exception as e:
            self.logger.error(f'error: updating status: {e}')

    def set_lamp(self, w, color, alpha):
        clr_hex = colors.resolve_color(color, alpha=alpha, format='hex')
        w.set_color(bg=clr_hex, fg='black')

    def update_precip(self, status_dct):

        precip = status_dct[aliases['precip']]
        precip_time = status_dct[aliases['precip_time']]

        cur_time = time.time()
        time_diff = cur_time - precip_time
        self.logger.debug(f'now={cur_time}, precip_time={precip_time}, diff={time_diff}')

        if precip in ERROR or (time_diff > stale_time_sec):
            self.logger.debug(f'no precip. {precip}')
            self.set_lamp(self.w.lamp_wet, clr_status['warning'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['warning'], 1.0)
        elif precip.upper() == "WET":
            self.logger.debug(f'precip is wet. {precip}')
            self.set_lamp(self.w.lamp_wet, clr_status['alarm'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['off'], 1.0)
        elif precip.upper() == "DRY":
            self.logger.debug(f'precip is dry. {precip}')
            self.set_lamp(self.w.lamp_wet, clr_status['off'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['normal'], 0.3)
        else:  # precip got weird value
            self.logger.debug(f'precip has weird value. {precip}')
            self.set_lamp(self.w.lamp_wet, clr_status['alarm'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['alarm'], 1.0)
