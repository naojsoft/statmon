#
# EnvMon.py -- Environmental monitor #1 plugin for StatMon
#
# E. Jeschke
#
import os
import time
import numpy as np

from ginga.gw import Viewers
from ginga.plot.plotaide import PlotAide
from ginga.canvas.types import plots as gplots
from ginga.plot import time_series as tsp
from ginga.plot import data_source as dsp
from ginga.misc import Bunch

import PlBase
from EnvMon3 import cross_connect_plots, make_plot

# For "envmon" plugin
al_envmon = dict(windd = ['TSCL.WINDD', 'STATS.AZ_ADJ'],
                 winds = ['TSCL.WINDS_O', 'TSCL.WINDS_I'],
                 temp = ['TSCL.TEMP_O', 'TSCL.TEMP_I'],
                 humid = ['STATL.HUMI_O.MEAN', 'TSCL.HUMI_I'],
                 m1dew = ['STATL.M1_TEMP_MIN', 'STATL.TRUSS_TEMP_MIN', 'STATL.DEW_POINT_TLSCP', 'STATL.DEW_POINT_CATWALK.MEAN'],
                 topring = ['TSCL.TOPRING_WINDS_F', 'TSCL.TOPRING_WINDS_R'],
                 misc = ['GEN2.STATUS.TBLTIME.TSCL'])

# starting dimensions of graph window (can change with window size)
dims = (500, 200)

# maximum number of data points to plot and save
num_pts = int(24 * 60 * 60)      # 24 hours worth

# interval (secs) between plot visual updates
# NOTE: this is independent of the rate at which data is saved
update_interval = 5.0

# interval (secs) between dataset flush to disk
save_interval = 10.0 * 60.0   # every 10 minutes

# initialize graphs to show back this time period from current time
show_last_time = 4.0 * 60 * 60

# outside, dome
plot_colors = ['darkviolet', 'palegreen4']


class EnvMon(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(2, 2, 2, 2)
        self.root.set_spacing(2)

        self.alias_d = {}

        self.plots = Bunch.Bunch()
        self.update_time = time.time()
        self.save_time = time.time()

        names = ["Outside", "Dome"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['windd'], num_pts,
                        y_acc=np.mean, title="Wind Dir N:0 E:90")
        self.root.add_widget(res.widget, stretch=1)
        self.plots.wind_direction = res

        names = ["Outside", "Dome"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['winds'], num_pts,
                        y_acc=np.mean, title="Windspeed (m/s)",
                        warn_y=7.0, alert_y=19.9)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.wind_speed = res

        names = ["Outside", "Dome"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['temp'], num_pts,
                        y_acc=np.mean, title="Temperature (C)")
        self.root.add_widget(res.widget, stretch=1)
        self.plots.temperature = res

        names = ["Outside", "Dome"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['humid'], num_pts,
                        y_acc=np.mean, title="Humidity (%)",
                        warn_y=70.0, alert_y=80.0)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.humidity = res

        names = ["M1", "T", "D (I)", "D (O)"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['m1dew'], num_pts,
                        y_acc=np.mean, title="M T & D (C)",
                        alert_y=5.0)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.m1_and_dew = res

        plot_bg = res.aide.get_plot_decor('plot_bg')
        plot_bg.check_warning = self.check_warning_m1dew

        names = ["Front", "Rear"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['topring'], num_pts,
                        y_acc=np.mean, title="TopRing WS",
                        alert_y=2.0)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.topring_windspeed = res

        cross_connect_plots(self.plots.values())

        self.gui_up = True

    def check_warning_m1dew(self):
        """custom warning check for m1 dew point."""
        bnch = self.plots.m1_and_dew
        m1, trs, dew_i, dew_o = bnch.sources

        # peek at last point of data sources for M1 and Dew Pt
        m_pt = m1.peek()
        trs_pt = trs.peek()
        d_i_pt = dew_i.peek()
        d_o_pt = dew_o.peek()
        if m_pt is None or trs_pt is None or d_o_pt is None or d_i_pt is None:
            return
        t, m1_temp_C = m_pt
        t, trs_temp_C = trs_pt
        t, dew_i_pt_temp_C = d_i_pt
        t, dew_o_pt_temp_C = d_o_pt
        self.logger.info(f"m1: {m1_temp_C} trs: {trs_temp_C} dew_i: {dew_i_pt_temp_C} dew_o: {dew_o_pt_temp_C}")

        plot_bg = bnch.aide.get_plot_decor('plot_bg')
        if m1_temp_C - dew_o_pt_temp_C <= 2.0 or m1_temp_C - dew_i_pt_temp_C <= 2.0 or trs_temp_C - dew_o_pt_temp_C <= 2.0  or trs_temp_C - dew_i_pt_temp_C <= 2.0:
            plot_bg.warning()
        else:
            plot_bg.normal()

    def start(self):
        aliases = []
        for name, _aliases in al_envmon.items():
            aliases.extend(_aliases)

        home_dir = os.path.join(os.environ['HOME'], '.statmon')
        if not os.path.isdir(home_dir):
            os.mkdir(home_dir)
        self.save_file = os.path.join(home_dir, "statmon_envmon.npy")
        try:
            d = np.load(self.save_file, allow_pickle=True)
            self.cst = dict(d[()])
        except Exception as e:
            self.logger.error("Couldn't open persist file: {}".format(e))
            self.cst = dict()

        t = time.time()

        for alias in aliases:

            if alias in self.alias_d:
                # create a array for this alias if we don't have one
                if alias not in self.cst:
                    self.cst[alias] = np.zeros((0, 2), dtype=float)

                points = self.cst[alias]
                bnch = self.alias_d[alias]
                bnch.dsrc.set_points(points)
                dsp.update_plot_from_source(bnch.dsrc, bnch.plot,
                                            update_limits=True)

                bnch.aide.update_plots()
                bnch.aide.zoom_limit_x(t - show_last_time, t)

        self.update_plots()

        self.controller.register_select(str(self), self.update, aliases)

    def stop(self):
        self.update_persist()

    def update(self, statusDict):
        t = statusDict.get('GEN2.STATUS.TBLTIME.TSCL', time.time())
        #t = statusDict.get('FITS.SBR.EPOCH', time.time())
        self.logger.debug("status update t={}".format(t))

        try:
            for alias in self.alias_d.keys():

                if alias in statusDict:
                    val = statusDict[alias]
                    if isinstance(val, float):
                        pt = (t, val)

                        bnch = self.alias_d[alias]
                        bnch.dsrc.add(pt)
                        dsp.update_plot_from_source(bnch.dsrc, bnch.plot,
                                                    update_limits=True)

            t = time.time()
            secs_since = t - self.update_time
            self.logger.debug("{0:.2f} secs since last plot update".format(secs_since))
            if secs_since >= update_interval:
                self.update_plots()

            secs_since = t - self.save_time
            self.logger.debug("{0:.2f} secs since last persist update".format(secs_since))
            if t - self.save_time >= save_interval:
                self.update_persist()

        except Exception as e:
            self.logger.error("error updating from status: {}".format(e),
                              exc_info=True)

    def update_plots(self):
        t = time.time()
        self.update_time = t
        self.logger.debug('updating plots')
        for bnch in self.plots.values():
            bnch.aide.update_plots()
        t1 = time.time()
        self.logger.debug("time to update plots {0:.4f} sec".format(t1 - t))

    def update_persist(self):
        t = time.time()
        self.save_time = t
        self.logger.debug('persisting data')
        # Ugh. It seems we have to reassign the arrays into the chest
        # every time, otherwise the additions to the array do not persist
        # in the chest when it is flushed
        # Double Ugh. Seems Chest does not have an update() method
        for alias, bnch in self.alias_d.items():
            self.cst[alias] = bnch.dsrc.get_points()

        try:
            np.save(self.save_file, self.cst, allow_pickle=True)
        except Exception as e:
            self.logger.error("Error saving array state: {}".format(e),
                              exc_info=True)
        t1 = time.time()
        self.logger.debug("time to persist data {0:.4f} sec".format(t1 - t))

    def __str__(self):
        return 'envmon'
