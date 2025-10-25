#
# DomeffPlugin.py -- dome flats plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
import time

from ginga.gw import Widgets
from ginga.misc import Bunch

from g2cam.INS import INSdata

import PlBase


clr_status = dict(off='white', normal='black', warning='orange', alarm='red')

monitor_time = {
    'obcp': Bunch.Bunch(last_time=0.0, timedelta=120),
    'tscs': Bunch.Bunch(last_time=0.0, timedelta=10),
    'tscl': Bunch.Bunch(last_time=0.0, timedelta=10),
    'tscv': Bunch.Bunch(last_time=0.0, timedelta=120),
    'mon': Bunch.Bunch(last_time=0.0, timedelta=10),
}


class StatusTablePlugin(PlBase.Plugin):
    """ StatusTable Plugin"""


    def __set_aliases(self, insname):

        self.insname = insname
        self.w.insname.set_text(insname)

        insdata = INSdata()
        try:
            inscode = insdata.getCodeByName(insname)
        except Exception as e:
            self.logger.error(f'error: fail to fetch inscode: {e}')
            inscode = 'SUK'

        self.inscode = inscode
        self.aliases = ['FITS.SBR.MAINOBCP',
                        'GEN2.STATUS.TBLTIME.{0}S0001'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0002'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0003'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0004'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0005'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0006'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0007'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0008'.format(inscode),
                        'GEN2.STATUS.TBLTIME.{0}S0009'.format(inscode),
                        'GEN2.STATUS.TBLTIME.TSCS',
                        'GEN2.STATUS.TBLTIME.TSCL',
                        'GEN2.STATUS.TBLTIME.TSCV']

        self.logger.info(f'aliases={str(self.aliases)}')

        self.controller.register_select('statustable', self.update,
                                        self.aliases)

    def build_gui(self, container):
        self.w = Bunch.Bunch()
        self.insname = 'SUKA'
        self.inscode = 'SUK'

        vbox = Widgets.VBox()
        vbox.set_border_width(4)

        gbox = Widgets.GridBox(rows=5, columns=2)
        gbox.set_border_width(2)
        gbox.set_row_spacing(2)
        self.w.insname = Widgets.Label("")
        gbox.add_widget(self.w.insname, 0, 0)
        self.w.insname_time = Widgets.Label("", halign='left')
        gbox.add_widget(self.w.insname_time, 0, 1)

        self.w.tscs = Widgets.Label("TSCS:")
        gbox.add_widget(self.w.tscs, 1, 0)
        self.w.tscs_time = Widgets.Label("", halign='left')
        gbox.add_widget(self.w.tscs_time, 1, 1)

        self.w.tscl = Widgets.Label("TSCL:")
        gbox.add_widget(self.w.tscl, 2, 0)
        self.w.tscl_time = Widgets.Label("", halign='left')
        gbox.add_widget(self.w.tscl_time, 2, 1)

        self.w.tscv = Widgets.Label("TSCV:")
        gbox.add_widget(self.w.tscv, 3, 0)
        self.w.tscv_time = Widgets.Label("", halign='left')
        gbox.add_widget(self.w.tscv_time, 3, 1)

        self.w.mon = Widgets.Label("MONITOR:")
        gbox.add_widget(self.w.mon, 4, 0)
        self.w.mon_time = Widgets.Label("", halign='left')
        gbox.add_widget(self.w.mon_time, 4, 1)

        vbox.add_widget(gbox, stretch=0)
        vbox.add_widget(Widgets.Label(""), stretch=1)

        container.add_widget(vbox, stretch=0)

        try:
            insname = self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')

        except Exception as e:
            self.logger.error(f'error: building layout: {e}')
        else:
            self.__set_aliases(insname)

    def start(self):
        self.controller.register_select('statustable', self.update, \
                                         self.aliases)
        self.controller.add_callback('change-config', self.change_config)

    def change_config(self, controller, d):
        insname = d['inst']
        if insname.startswith('#'):
            self.logger.debug(f'obcp is not assigned: {insname}')
            return

        self.logger.debug(f"target changing config dict={str(d)} ins={insname}")
        self.__set_aliases(insname)

    def update(self, status_dct):
        self.logger.info(f'status={str(status_dct)}')
        try:
            self.update_table(status_dct)

        except Exception as e:
            self.logger.error(f"error updating status table times: {e}",
                              exc_info=True)

    def update_table(self, status_dct):
        global monitor_time

        cur_time = time.time()

        for i, name in enumerate(['tscs', 'tscl', 'tscv']):
            tsc_time = status_dct.get(self.aliases[i + 10])
            tsc_time_str = time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(tsc_time))
            monitor_time[name].last_time = tsc_time
            color = clr_status['normal']
            if cur_time - tsc_time > monitor_time[name].timedelta:
                color = clr_status['warning']
            self.w[f'{name}_time'].set_text(tsc_time_str)
            self.w[f'{name}_time'].set_color(fg=color)

        mon_time = self.controller.last_update
        self.logger.debug('mon last_update=%s' %str(mon_time))
        mon_time_str = time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.localtime(mon_time))
        monitor_time['mon'].last_time = mon_time
        color = clr_status['normal']
        if cur_time - mon_time > monitor_time['mon'].timedelta:
            color = clr_status['warning']
        self.w.mon_time.set_text(mon_time_str)
        self.w.mon_time.set_color(fg=color)

        insname = status_dct['FITS.SBR.MAINOBCP']
        if self.insname != insname:
            # <-- instrument names don't match
            self.__set_aliases(insname)
            # will update instrument table times at next fetch
            return

        obcp_times = [status_dct.get(self.aliases[i], 0.0)
                      for i in range(1, 10)]
        self.logger.debug('obcp_times={}'.format(str(obcp_times)))
        obcp_times = list(filter(lambda n: isinstance(n, float), obcp_times))
        if len(obcp_times) == 0:
            obcp_time_str = "Undefined"
            obcp_time = monitor_time['obcp'].last_time
        else:
            # take the latest table time
            obcp_time = max(obcp_times)
            obcp_time_str = time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime(obcp_time))
        monitor_time['obcp'].last_time = obcp_time
        color = clr_status['normal']
        if cur_time - obcp_time > monitor_time['obcp'].timedelta:
            color = clr_status['warning']
        self.w.insname.set_text(f"{self.insname}:")
        self.w.insname_time.set_text(obcp_time_str)
        self.w.insname_time.set_color(fg=color)
