#
# DomeffPlugin.py -- dome flats plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
from ginga.gw import Widgets, GwHelp
from ginga.misc import Bunch
from ginga import colors

import PlBase


clr_status = dict(off='white',
                  normal='forestgreen',
                  normal_bg='green',
                  warning='orange',
                  alarm='red')
pwr_vals = dict(on=1, off=2)
font = ("Sans", 11)

aliases = dict(ff_a='TSCV.DomeFF_A',
               ff_1b='TSCV.DomeFF_1B',
               ff_2b='TSCV.DomeFF_2B',
               ff_3b='TSCV.DomeFF_3B',
               ff_4b='TSCV.DomeFF_4B',
               ff_a_v='TSCL.DOMEFF_A_VOL',
               ff_1b_v='TSCL.DOMEFF_1B_VOL',
               ff_2b_v='TSCL.DOMEFF_2B_VOL',
               ff_3b_v='TSCL.DOMEFF_3B_VOL',
               ff_4b_v='TSCL.DOMEFF_4B_VOL')


class DomeffPlugin(PlBase.Plugin):
    """ Dome 600W and 10W lamps """

    def build_gui(self, container):

        self.font = GwHelp.get_font("Sans Bold", 11)
        self.w = Bunch.Bunch()

        gbox = Widgets.GridBox(rows=3, columns=6)
        gbox.set_border_width(2)
        gbox.set_row_spacing(4)
        gbox.add_widget(self._get_label("DomeFF:"), 0, 0)
        self.w.lamp_600w = self._get_label("600W", halign='center')
        self.w.lamp_600w.set_font(font[0], size=font[1])
        gbox.add_widget(self.w.lamp_600w, 0, 1)
        self.set_lamp(self.w.lamp_600w, clr_status['off'], 1.0)
        self.w.lamp_10w = self._get_label("10W", halign='center')
        self.w.lamp_10w.set_font(font[0], size=font[1])
        gbox.add_widget(self.w.lamp_10w, 0, 3)
        self.set_lamp(self.w.lamp_10w, clr_status['off'], 1.0)

        gbox.add_widget(self._get_label("A:", halign='center'), 1, 1)
        gbox.add_widget(self._get_label("1B:", halign='center'), 1, 2)
        gbox.add_widget(self._get_label("2B:", halign='center'), 1, 3)
        gbox.add_widget(self._get_label("3B:", halign='center'), 1, 4)
        gbox.add_widget(self._get_label("4B:", halign='center'), 1, 5)
        self.w.ff_a_v = self._get_label("", halign='center')
        gbox.add_widget(self.w.ff_a_v, 2, 1)
        self.w.ff_1b_v = self._get_label("", halign='center')
        gbox.add_widget(self.w.ff_1b_v, 2, 2)
        self.w.ff_2b_v = self._get_label("", halign='center')
        gbox.add_widget(self.w.ff_2b_v, 2, 3)
        self.w.ff_3b_v = self._get_label("", halign='center')
        gbox.add_widget(self.w.ff_3b_v, 2, 4)
        self.w.ff_4b_v = self._get_label("", halign='center')
        gbox.add_widget(self.w.ff_4b_v, 2, 5)

        container.add_widget(gbox, stretch=0)

    def start(self):
        self.controller.register_select('domeff', self.update,
                                        list(aliases.values()))

    def _get_label(self, name, halign=None):
        lbl = Widgets.Label(name, halign=halign)
        lbl.set_font(self.font)
        lbl.set_color(fg=clr_status['normal'])
        return lbl

    def update(self, status_dct):
        self.logger.debug('status=%s' % str(status_dct))
        try:
            self.update_power(status_dct)

            self.update_voltage(status_dct)

        except Exception as e:
            self.logger.error(f"error: updating status: {e}")

    ###### VOLTAGE ######

    def update_voltage(self, status_dct):

        for name in ['ff_a_v', 'ff_1b_v', 'ff_2b_v', 'ff_3b_v', 'ff_4b_v']:
            voltage = status_dct[aliases[name]]
            value, color = self._validate_voltage(voltage)
            lbl_w = self.w[name]
            lbl_w.set_text(value)
            lbl_w.set_color(bg=color, fg='black')

    def _validate_voltage(self, voltage):
        try:
            val = f'{voltage:.1f}V'
            color = clr_status['off']
            if voltage > 0.0:
                color = clr_status['normal_bg']
            res = (val, color)
        except Exception:
            val = 'Undef'
            res = (val, clr_status['alarm'])

        return res

    ###### POWER ######

    def update_power(self, status_dct):

        ff_a = status_dct[aliases['ff_a']]
        ff_1b = status_dct[aliases['ff_1b']]
        ff_2b = status_dct[aliases['ff_2b']]
        ff_3b = status_dct[aliases['ff_3b']]
        ff_4b = status_dct[aliases['ff_4b']]
        self.logger.debug(f'updating domeff a={ff_a}, 1b={ff_1b}, 2b={ff_2b}, 3b={ff_3b}, 4b={ff_4b}')

        # somehow, right shift is required for certain statas aliases
        # before shifting, converting hex to int is also done in this method
        ff_1b = self._shift_value(ff_1b)
        ff_2b = self._shift_value(ff_2b, shift=4)
        ff_4b = self._shift_value(ff_4b)
        self.logger.debug(f'shifted value a={ff_a}, 1b={ff_1b}, 2b={ff_2b}, 3b={ff_3b}, 4b={ff_4b}')

        num_on = [ff_a, ff_1b, ff_2b, ff_3b, ff_4b].count(pwr_vals['on'])
        self.logger.debug(f"number of on {num_on}")

        vals = set([ff_1b, ff_2b, ff_3b, ff_4b])
        num_undef = self._num_of_undef_vals(val_set=vals)
        self.logger.debug(f"number of undef={num_undef}")
        six00W = (ff_1b, ff_2b, ff_3b, ff_4b)
        self.logger.debug(f'ff_a={ff_a}, six00W={six00W}, num_undef={num_undef}, num_on={num_on}')

        if ff_a == pwr_vals['on']:
            self.logger.debug(f'ff_a is on. {ff_a}')
            self.set_lamp(self.w.lamp_10w, clr_status['normal_bg'], 0.3)
            if num_on > pwr_vals['on']:
                self.logger.debug(f"ff_a is on {ff_a}, but num_on > on {num_on} > {pwr_vals['on']}")
                self.set_lamp(self.w.lamp_10w, clr_status['warning'], 1.0)
        elif ff_a == pwr_vals['off']:
            self.logger.debug(f'ff_a is off. {ff_a}')
            self.set_lamp(self.w.lamp_10w, clr_status['off'], 1.0)
        else:
            self.logger.debug(f'ff_a is not on or off. {ff_a}')
            self.set_lamp(self.w.lamp_10w, clr_status['alarm'], 1.0)

        if num_undef: # there is some undef value in 600W, not on or off
            self.logger.debug(f'num_undef. {num_undef}')
            self.set_lamp(self.w.lamp_600w, clr_status['alarm'], 1.0)

        else:  # 600W is either on or off
            if pwr_vals['on'] in six00W:
                self.logger.debug(f'on in six00W. {six00W}')
                self.set_lamp(self.w.lamp_600w, clr_status['normal_bg'], 0.3)

                if num_on > pwr_vals['on']:
                    self.logger.debug(f"on in six00W {six00W}, but num_on > on {num_on} > {pwr_vals['on']}")
                    self.set_lamp(self.w.lamp_600w, clr_status['warning'], 1.0)
            else:  #  off
                self.logger.debug(f'on not in six00W. {six00W}')
                self.set_lamp(self.w.lamp_600w, clr_status['off'], 1.0)

    def set_lamp(self, w, color, alpha):
        clr_hex = colors.resolve_color(color, alpha=alpha, format='hex')
        w.set_color(bg=clr_hex, fg='black')

    def _shift_value(self, val, shift=2):
        ''' default right shift by 2  '''

        try:
            #val = int('%s' %(str(val)) , 16)
            val = val >> shift
        except Exception:
            val = None
        finally:
            return val

    def _num_of_undef_vals(self, val_set):

        for val in [pwr_vals['on'], pwr_vals['off']]:
            self.logger.debug(f'val to remove={val} val_set={val_set}')
            try:
                val_set.remove(val)
                self.logger.debug(f'val removed. val_set={val_set}')
            except KeyError:
                pass
        return len(val_set)
