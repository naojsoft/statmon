#
# CalprobePlugin.py -- Calibration Probe plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
from ginga.gw import Widgets, GwHelp
from ginga.misc import Bunch
from ginga import colors

import PlBase


clr_status = dict(off='white', normal='forestgreen', warning='orange', alarm='red')

aliases = ['TSCL.CAL_POS']


class CalprobePlugin(PlBase.Plugin):
    """ Cal Source Probe Plugin """

    def build_gui(self, container):
        self.font = GwHelp.get_font("Sans Bold", 11)
        self.w = Bunch.Bunch()

        gbox = Widgets.GridBox(rows=1, columns=4)
        gbox.set_border_width(2)
        gbox.set_column_spacing(4)
        gbox.add_widget(self._get_label("CalProbe:", halign='left'), 0, 0)
        self.w.probe_val = self._get_label("", halign='center')
        gbox.add_widget(self.w.probe_val, 0, 1)
        gbox.add_widget(Widgets.Label(""), 0, 2)  # spacer
        gbox.add_widget(Widgets.Label(""), 0, 3)  # spacer

        container.add_widget(gbox, stretch=0)

    def start(self):
        self.controller.register_select('calprobe', self.update, aliases)

    def _get_label(self, name, halign=None):
        lbl = Widgets.Label(name, halign=halign)
        lbl.set_font(self.font)
        lbl.set_color(fg=clr_status['normal'])
        return lbl

    def update(self, status_dct):
        self.logger.debug('status=%s' % str(status_dct))
        try:
            self.update_calprobe(status_dct)

        except Exception as e:
            self.logger.error(f'error: updating status: {e}')

    def update_calprobe(self, status_dct):
        ''' probe = TSCL.CAL_POS '''

        probe = status_dct[aliases[0]]
        self.logger.debug(f'probe={probe}')

        color = clr_status['normal']
        try:
            text = f'{probe:+3.3f} mm'
            self.w.probe_val.set_color(fg=clr_status['normal'])

        except Exception:
            text = 'Undefined'
            self.w.probe_val.set_color(fg=clr_status['alarm'])
            self.logger.error(f'error: calprobe undef. probe={probe}')

        self.w.probe_val.set_text(text)
