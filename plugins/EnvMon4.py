#
# EnvMon4.py -- Environmental monitor #2 plugin for StatMon
#
# Eric Jeschke (eric@naoj.org)
#
import os
import time
import numpy as np

import ginga.toolkit as ginga_toolkit
from ginga.gw import Viewers
from ginga.plot.plotaide import PlotAide
from ginga.canvas.types import plots as gplots
from ginga.plot import time_series as tsp
from ginga.plot import data_source as dsp
from ginga.misc import Bunch

from qtpy import QtWidgets, QtCore, QtGui

from chest import Chest

import PlBase
from EnvMon3 import cross_connect_plots, make_plot

# For "envmon2" plugin
al_envmon = dict(windd = ['TSCL.WINDD', 'STATS.AZ_ADJ'],
                 winds = ['TSCL.WINDS_O', 'TSCL.WINDS_I'],
                 winds_roof = ['TSCL.ROOF_WINDS_IR_F',
                               'TSCL.ROOF_WINDS_OPT_F',
                               'TSCL.ROOF_WINDS_R'],
                 wind_gust = ['TSCL.WIND_MAX_SPEED'],
                 topring = ['TSCL.TOPRING_WINDS_F', 'TSCL.TOPRING_WINDS_R'],
                 ctr_winds = ['STATL.CSCT_WINDS_MAX'],
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

plot_colors = ['darkviolet', 'palegreen4', 'darkbrown']


class EnvMon4(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        #self.root.setStyleSheet("QWidget { background: lightblue }")

        self.alias_sets = [al_envmon[key] for key in al_envmon]
        self.alias_d = {}

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        container.setLayout(layout)

        self.plots = Bunch.Bunch()
        self.update_time = time.time()
        self.save_time = time.time()

        names = ["Outside", "Dome"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['windd'], num_pts,
                        y_acc=np.mean, title="Wind Dir N:0 E:90")
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.wind_direction = res

        names = ["Outside", "Dome"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['winds'], num_pts,
                        y_acc=np.mean, title="Windspeed (m/s)",
                        warn_y=7.0, alert_y=19.9)
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.wind_speed = res

        names = ["Roof IR(F)", "Roof Opt(F)", "Roof (R)"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['winds_roof'], num_pts,
                        y_acc=np.mean, title="Roof Windspeed (m/s)",
                        warn_y=7.0, alert_y=19.9)
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.roof_wind_speed = res

        names = ["Wind Gust"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['wind_gust'], num_pts,
                        y_acc=np.mean, title="Wind Speed Gust")
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.windspeed_gust = res

        names = ["Front", "Rear"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['topring'], num_pts,
                        y_acc=np.mean, title="TopRing WS",
                        alert_y=2.0)
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.topring_windspeed = res

        names = ["Center"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon['ctr_winds'], num_pts,
                        y_acc=np.mean, title="Wind Speed Center",
                        alert_y=2.0)
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.windspeed_center = res

        cross_connect_plots(self.plots.values())

        self.gui_up = True

    def start(self):
        aliases = []
        for name, _aliases in al_envmon.items():
            aliases.extend(_aliases)

        env2file = os.path.join(os.environ['GEN2COMMON'], 'db',
                                "envmon_envmon4.cst")
        self.cst = Chest(path=env2file)

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
            self.cst.flush()
        except Exception as e:
            self.logger.error("Error saving chest file: {}".format(e),
                              exc_info=True)
        t1 = time.time()
        self.logger.debug("time to persist data {0:.4f} sec".format(t1 - t))

    def __str__(self):
        return 'envmon4'
