#
# EnvMon4.py -- Environmental monitor #2 plugin for StatMon
#
# E. Jeschke
#
import os
import time
import numpy as np

from ginga.plot import data_source as dsp
from ginga.misc import Bunch

import PlBase
from EnvMon3 import cross_connect_plots, make_plot

# For "envmon4" plugin
al_envmon = dict(windd=['TSCL.WINDD', 'STATS.AZ_ADJ'],
                 winds=['TSCL.WINDS_O', 'TSCL.WINDS_I'],
                 winds_roof=['TSCL.ROOF_WINDS_IR_F',
                             'TSCL.ROOF_WINDS_OPT_F',
                             'TSCL.ROOF_WINDS_R'],
                 wind_gust=['TSCL.WIND_MAX_SPEED'],
                 topring=['TSCL.TOPRING_WINDS_F', 'TSCL.TOPRING_WINDS_R'],
                 ctr_winds=['STATL.CSCT_WINDS_MAX'],
                 part=['GEN2.PART.ELVTOWER.NC_ALL',
                       'GEN2.PART.OBSFLOOR.NC_ALL'],
                 misc=['GEN2.STATUS.TBLTIME.TSCL'])

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

plot_colors = ['darkviolet', 'palegreen4', 'darkbrown']


class EnvMon4(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(2, 2, 2, 2)
        self.root.set_spacing(2)

        self.alias_sets = [al_envmon[key] for key in al_envmon]
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

        names = ["IR(F)", "Opt(F)", "Rear"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['winds_roof'], num_pts,
                        y_acc=np.mean, title="Roof WS(m/s)",
                        warn_y=7.0, alert_y=19.9)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.roof_wind_speed = res

        names = ["Wind Gust"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['wind_gust'], num_pts,
                        y_acc=np.mean, title="Wind Speed Gust")
        self.root.add_widget(res.widget, stretch=1)
        self.plots.windspeed_gust = res

        names = ["Front", "Rear"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['topring'], num_pts,
                        y_acc=np.mean, title="TopRing WS",
                        alert_y=2.0)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.topring_windspeed = res

        names = ["Center"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['ctr_winds'], num_pts,
                        y_acc=np.mean, title="Wind Speed Center",
                        alert_y=2.0)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.windspeed_center = res

        names = ["Tower", "ObsFloor"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['part'], num_pts,
                        y_acc=np.mean, title="Particulates",
                        warn_y=25.0, alert_y=30.0)
        self.root.add_widget(res.widget, stretch=1)
        self.plots.windspeed_center = res

        cross_connect_plots(self.plots.values())

        self.gui_up = True

    def start(self):
        aliases = []
        for name, _aliases in al_envmon.items():
            aliases.extend(_aliases)

        home_dir = os.path.join(os.environ['HOME'], '.statmon')
        if not os.path.isdir(home_dir):
            os.mkdir(home_dir)
        self.save_file = os.path.join(home_dir,
                                      f"{self.controller.name}_{str(self)}.npy")  # noqa
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
            self.logger.debug("{0:.2f} secs since last plot update".format(secs_since))  # noqa
            if secs_since >= update_interval:
                self.update_plots()

            secs_since = t - self.save_time
            self.logger.debug("{0:.2f} secs since last persist update".format(secs_since))  # noqa
            if t - self.save_time >= save_interval:
                self.update_persist()

        except Exception as e:
            self.logger.error("error updating from status: {}".format(e),
                              exc_info=True)

    def update_plots(self):
        t = time.time()
        self.update_time = t
        self.logger.debug('updating plots')
        for plot in self.plots.values():
            plot.aide.update_plots()
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
        return 'envmon4'
