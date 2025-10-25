#
# CalPlugin.py -- calibration lamps plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
from ginga.gw import Widgets
from ginga.misc import Bunch
from ginga import colors

from g2cam.status.common import STATNONE, STATERROR
ERROR = ["Unknown", None, STATNONE, STATERROR, 'None']

import PlBase

clr_status = dict(off='white', normal='green', warning='orange', alarm='red')
pwr_vals = dict(on=1, off=2)

aliases = dict(hct1='TSCV.CAL_HCT_LAMP1', hct2='TSCV.CAL_HCT_LAMP2',
               hal1='TSCV.CAL_HAL_LAMP1', hal2='TSCV.CAL_HAL_LAMP2',
               rgl1='TSCV.CAL_RGL_LAMP1', rgl2='TSCV.CAL_RGL_LAMP2',
               hct1_amp='TSCL.CAL_HCT1_AMP', hct2_amp='TSCL.CAL_HCT2_AMP',
               hal1_amp='TSCL.CAL_HAL1_AMP', hal2_amp='TSCL.CAL_HAL2_AMP')


class CalPlugin(PlBase.Plugin):
    """ Cal Source Plugin """

    def build_gui(self, container):

        self.w = Bunch.Bunch()

        gbox = Widgets.GridBox(rows=2, columns=4)
        gbox.set_row_spacing(4)
        gbox.set_border_width(2)
        gbox.add_widget(Widgets.Label("Calib:"), 0, 0)

        self.w.lamp_th_ar1 = Widgets.Label("Th-Ar1", halign='center')
        gbox.add_widget(self.w.lamp_th_ar1, 0, 1)
        self.set_lamp(self.w.lamp_th_ar1, clr_status['off'], 1.0)
        self.w.lamp_ne = Widgets.Label("Ne", halign='center')
        gbox.add_widget(self.w.lamp_ne, 0, 2)
        self.set_lamp(self.w.lamp_ne, clr_status['off'], 1.0)
        self.w.lamp_hal1 = Widgets.Label("Hal1", halign='center')
        gbox.add_widget(self.w.lamp_hal1, 0, 3)
        self.set_lamp(self.w.lamp_hal1, clr_status['off'], 1.0)

        self.w.lamp_th_ar2 = Widgets.Label("Th-Ar2", halign='center')
        gbox.add_widget(self.w.lamp_th_ar2, 1, 1)
        self.set_lamp(self.w.lamp_th_ar2, clr_status['off'], 1.0)
        self.w.lamp_ar = Widgets.Label("Ar", halign='center')
        gbox.add_widget(self.w.lamp_ar, 1, 2)
        self.set_lamp(self.w.lamp_ar, clr_status['off'], 1.0)
        self.w.lamp_hal2 = Widgets.Label("Hal2", halign='center')
        gbox.add_widget(self.w.lamp_hal2, 1, 3)
        self.set_lamp(self.w.lamp_hal2, clr_status['off'], 1.0)

        self.w.ma = Widgets.Label("", halign='center')
        gbox.add_widget(self.w.ma, 1, 0)

        container.add_widget(gbox, stretch=0)

    def start(self):
        self.controller.register_select('cal', self.update,
                                         list(aliases.values()))

    def update(self, status_dct):
        self.logger.debug('status=%s' % str(status_dct))
        try:
            self.update_cal_lamps(status_dct)

        except Exception as e:
            self.logger.error(f"error: updating status: {e}")

    def update_cal_lamps(self, status_dct):
        ''' hct1 = TSCV.CAL_HCT_LAMP1
            hct2 = TSCV.CAL_HCT_LAMP2
            hal1 = TSCV.CAL_HAL_LAMP1
            hal2 = TSCV.CAL_HAL_LAMP2
            rgl1 = TSCV.CAL_RGL_LAMP1
            rgl2 = TSCV.CAL_RGL_LAMP2

            hal1_amp = TSCL.CAL_HAL1_AMP
            hal2_amp = TSCL.CAL_HAL2_AMP
            hct1_amp = TSCL.CAL_HCT1_AMP
            hct2_amp = TSCL.CAL_HCT2_AMP
        '''
        # hct1 = (hct1_cs, hct1_nsopt, hct1_pf1, hct1_pf2)
        # hct2 = (hct2_cs, hct2_nsopt)
        # hal1 = (hal1_cs, hal1_nsopt, hal1_nsir)
        # hal2 = (hal2_cs, hal2_nsopt, hal2_nsir)
        # rgl1 = (rgl1_cs, rgl1_nsir)
        # rgl2 = (rgl2_cs, rgl2_nsir)
        hct1 = status_dct[aliases['hct1']]
        hct2 = status_dct[aliases['hct2']]
        hal1 = status_dct[aliases['hal1']]
        hal2 = status_dct[aliases['hal2']]
        rgl1 = status_dct[aliases['rgl1']]
        rgl2 = status_dct[aliases['rgl2']]
        hct1_amp = status_dct[aliases['hct1_amp']]
        hct2_amp = status_dct[aliases['hct2_amp']]
        hal1_amp = status_dct[aliases['hal1_amp']]
        hal2_amp = status_dct[aliases['hal2_amp']]
        # NOTE: these were kwargs in the previous version, default None
        # but no value was passed for them so they are None here
        # ....EJ
        rgl1_amp = None
        rgl2_amp = None

        self.logger.debug(f'updating hct1={hct1}, hct2={hct2}, hal1={hal1}, hal2={hal2}, rgl1={rgl1}, rgl2={rgl2}')

        hct1_cs = self.__shift_value(hct1, focus='CS')
        hct1_nsopt = self.__shift_value(hct1, focus='NSOPT')
        hct1_pf1 = self.__shift_value(hct1, focus='PF1')
        hct1_pf2 = self.__shift_value(hct1, focus='PF2')

        hct2_cs = self.__shift_value(hct2, focus='CS')
        hct2_nsopt = self.__shift_value(hct2, focus='NSOPT')

        hal1_cs = self.__shift_value(hal1, focus='CS')
        hal1_nsopt = self.__shift_value(hal1, focus='NSOPT')
        hal1_nsir = self.__shift_value(hal1, focus='NSIR')

        hal2_cs = self.__shift_value(hal2, focus='CS')
        hal2_nsopt = self.__shift_value(hal2, focus='NSOPT')
        hal2_nsir = self.__shift_value(hal2, focus='NSIR')

        rgl1_cs = self.__shift_value(rgl1, focus='CS')
        rgl1_nsir = self.__shift_value(rgl1, focus='NSIR')

        rgl2_cs = self.__shift_value(rgl2, focus='CS')
        rgl2_nsir = self.__shift_value(rgl2, focus='NSIR')


        bhct1 = Bunch.Bunch(lamp=(hct1_cs, hct1_nsopt, hct1_pf1, hct1_pf2), amp=hct1_amp)
        bhct2 = Bunch.Bunch(lamp=(hct2_cs, hct2_nsopt), amp=hct2_amp)
        bhal1 = Bunch.Bunch(lamp= (hal1_cs, hal1_nsopt, hal1_nsir), amp=hal1_amp)
        bhal2 = Bunch.Bunch(lamp=(hal2_cs, hal2_nsopt, hal2_nsir), amp=hal2_amp)
        brgl1 = Bunch.Bunch(lamp=(rgl1_cs, rgl1_nsir), amp=rgl1_amp)
        brgl2 = Bunch.Bunch(lamp=(rgl2_cs, rgl2_nsir), amp=rgl2_amp)

        lamp_lst = [(self.w.lamp_th_ar1, bhct1),
                    (self.w.lamp_th_ar2, bhct2),
                    (self.w.lamp_hal1, bhal1),
                    (self.w.lamp_hal2, bhal2),
                    (self.w.lamp_ne, brgl1),
                    (self.w.lamp_ar, brgl2),
                    ]

        self.logger.debug('shifted hct1cs={hct1_cs}, htc1nsopt={hct1_nsopt}, hct1pf1={hct1_pf1}, hct1pf2={hct1_pf2}')

        lamps = [hct1_cs, hct1_nsopt, hct1_pf1, hct1_pf2, hct2_cs, hct2_nsopt,
                 hal1_cs, hal1_nsopt, hal1_nsir, hal2_cs, hal2_nsopt, hal2_nsir,
                 rgl1_cs, rgl1_nsir, rgl2_cs, rgl2_nsir]

        num_on = lamps.count(pwr_vals['on'])

        for lamp, val in lamp_lst:
            vals = set(val.lamp)
            num_undef = self.__num_of_undef_vals(val_set=vals)

            self.logger.debug(f'lamps  {vals}')
            self.logger.debug(f'num undef {num_undef}')

            if num_undef:
                self.set_lamp(lamp, clr_status['alarm'], 1.0)
            else:
                self.logger.debug(f'val lamp {val.lamp}')
                self.logger.debug(f'val amp {val.amp}')
                ma = ''
                if pwr_vals['on'] in val.lamp:
                    self.set_lamp(lamp, clr_status['normal'], 0.5)
                    self.logger.debug('on')

                    self.logger.debug(f'val amp={val.amp}')

                    if num_on > pwr_vals['on']: # at least 2 lamps are on
                        self.set_lamp(lamp, clr_status['warning'], 1.0)
                    else: # 1 lamp is on
                        if not val.amp in ERROR:
                            ma = '%+5.3fmA' % val.amp
                        self.w.ma.set_text(ma)
                        self.logger.debug(f'amp={ma}')
                else:
                    self.logger.debug('off')
                    #if not ma:
                    #    self.w.ma.set_text(ma)
                    self.set_lamp(lamp, clr_status['off'], 1.0)


    def set_lamp(self, w, color, alpha):
        clr_hex = colors.resolve_color(color, alpha=alpha, format='hex')
        w.set_color(bg=clr_hex, fg='black')

    def __num_of_undef_vals(self, val_set):
        ''' find out the number of undefined values'''

        for val in [pwr_vals['on'], pwr_vals['off']]:
            if val in val_set:
                val_set.remove(val)
        return len(val_set)

    def __mask_value(self, val, focus):

        mask = {'CS': 0x03, 'NSIR': 0x30, 'NSOPT': 0x0c,
                'PF1': 0x30, 'PF2': 0xc0}
        try:
            #val = int('%s' %val, 16)
            val = val & mask[focus]
        except Exception:
            val = None
        finally:
            return val

    def __shift_value(self, val, focus):
        ''' right shift '''
        shift = {'CS': 0, 'NSIR': 4, 'NSOPT': 2, 'PF1': 4, 'PF2': 6}

        masked = self.__mask_value(val, focus)

        try:
            val = masked >> shift[focus]
        except Exception:
            val = None
        finally:
            return val
