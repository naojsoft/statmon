#
# PrecipPlugin.py -- precipitation sensor monitoring plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
import os.path
import time
from datetime import timedelta
import json

from ginga.gw import Widgets, GwHelp
from ginga.misc import Bunch
from ginga import colors

from g2cam.status.common import STATNONE, STATERROR
ERROR = ["Unknown", None, STATNONE, STATERROR, 'None']

import PlBase


clr_status = dict(off='white',
                  normal='forestgreen',
                  normal_bg='green',
                  warning='orange',
                  alarm='red')

aliases = dict(precip='GEN2.PRECIP.SENSOR1.STATUS',
               precip_time='GEN2.PRECIP.SENSOR1.TIME',
               clock='FITS.SBR.EPOCH')

# How long if we haven't heard from the precipitation sensor that we
# consider it stale
stale_time_sec = 60


class PrecipPlugin(PlBase.Plugin):
    """ Precip """

    def build_gui(self, container):
        self.font = GwHelp.get_font("Sans Bold", 11)
        self.w = Bunch.Bunch()
        self.save_dct = dict(last_wet_time_sec=None)

        gbox = Widgets.GridBox(rows=2, columns=5)
        gbox.set_border_width(2)
        gbox.add_widget(self._get_label("Precip:"), 0, 0)
        self.w.lamp_wet = self._get_label("Wet", halign='center')
        gbox.add_widget(self.w.lamp_wet, 0, 1)
        self.set_lamp(self.w.lamp_wet, clr_status['off'], 1.0)
        self.w.lamp_dry = self._get_label("Dry", halign='center')
        gbox.add_widget(self.w.lamp_dry, 0, 2)
        self.set_lamp(self.w.lamp_dry, clr_status['off'], 1.0)
        self.w.precip_time = self._get_label("", halign='left')
        gbox.add_widget(self.w.precip_time, 0, 3)
        gbox.add_widget(Widgets.Label(""), 0, 4)  # add spacer
        gbox.add_widget(self._get_label("Last wet:"), 1, 0)
        self.w.last_wet_time = self._get_label("", halign='left')
        self._get_last_wet_time()
        gbox.add_widget(self.w.last_wet_time, 1, 1)

        container.add_widget(gbox, stretch=0)

    def start(self):
        home_dir = os.path.join(os.environ['HOME'], '.statmon')
        if not os.path.isdir(home_dir):
            os.mkdir(home_dir)
        self.save_file = os.path.join(home_dir,
                                      f"{self.controller.name}_{str(self)}.json")
        try:
            with open(self.save_file, 'r') as in_f:
                self.save_dct = json.load(in_f)
                self._get_last_wet_time()

        except Exception as e:
            self.logger.error(f"Couldn't open persist file {self.save_file}: {e}")

        self.controller.register_select('precip', self.update,
                                        list(aliases.values()))

    def stop(self):
        try:
            with open(self.save_file, 'w') as out_f:
                out_f.write(json.dumps(self.save_dct))

        except Exception as e:
            self.logger.error(f"Couldn't write persist file {self.save_file}: {e}")

    def update(self, status_dct):
        self.logger.debug('status=%s' % str(status_dct))
        try:
            self.update_precip(status_dct)

        except Exception as e:
            self.logger.error(f'error: updating status: {e}')

    def _get_label(self, name, halign=None):
        lbl = Widgets.Label(name, halign=halign)
        lbl.set_font(self.font)
        lbl.set_color(fg=clr_status['normal'])
        return lbl

    def _get_last_wet_time(self):
        last_wet_time_sec = self.save_dct.get('last_wet_time_sec', None)
        last_wet_time_str = 'Unknown'
        if last_wet_time_sec is not None:
            last_wet_time_str = time.strftime("%m/%d %H:%M",
                                              time.localtime(last_wet_time_sec))
        self.w.last_wet_time.set_text(last_wet_time_str)
        return last_wet_time_str

    def set_lamp(self, w, color, alpha):
        clr_hex = colors.resolve_color(color, alpha=alpha, format='hex')
        w.set_color(bg=clr_hex, fg='black')

    def update_precip(self, status_dct):
        precip = status_dct[aliases['precip']]
        precip_time = status_dct[aliases['precip_time']]
        cur_time = time.time()
        if isinstance(precip_time, float):
            time_diff = cur_time - precip_time
            self.logger.debug(f'now={cur_time}, precip_time={precip_time}, diff={time_diff}')
        else:
            time_diff = 24 * 60 * 60
            self.logger.warning(f'precip_time={precip_time}')
        precip_time_s = str(timedelta(seconds=int(time_diff)))
        if time_diff > 0:
            precip_time_s = "-" + precip_time_s
        elif time_diff < 0:
            precip_time_s = "+" + precip_time_s
        self.w.precip_time.set_text(precip_time_s)

        if precip in ERROR or (time_diff > stale_time_sec):
            self.logger.debug(f'no precip. {precip}')
            #self.w.precip_time.set_color(fg=clr_status['alarm'])
            self.set_lamp(self.w.lamp_wet, clr_status['warning'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['warning'], 1.0)
        elif precip.upper() == "WET":
            if isinstance(precip_time, float):
                self.save_dct['last_wet_time_sec'] = precip_time
                self._get_last_wet_time()
            self.logger.debug(f'precip is wet. {precip}')
            #self.w.precip_time.set_color(fg=clr_status['normal'])
            self.set_lamp(self.w.lamp_wet, clr_status['alarm'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['off'], 1.0)
        elif precip.upper() == "DRY":
            self.logger.debug(f'precip is dry. {precip}')
            #self.w.precip_time.set_color(fg=clr_status['normal'])
            self.set_lamp(self.w.lamp_wet, clr_status['off'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['normal_bg'], 0.3)
        else:
            # precip got weird value
            self.logger.debug(f'precip has weird value. {precip}')
            #self.w.precip_time.set_color(fg=clr_status['warning'])
            self.set_lamp(self.w.lamp_wet, clr_status['alarm'], 1.0)
            self.set_lamp(self.w.lamp_dry, clr_status['alarm'], 1.0)

    def __str__(self):
        return 'precip'
