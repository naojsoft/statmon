#
# EnvMon3.py -- Environmental monitor #3 plugin for StatMon
#
# E. Jeschke
#
import os
import time
import numpy as np

import ginga.toolkit as ginga_toolkit
from ginga.misc import Bunch
from ginga.gw import Viewers
from ginga.plot.plotaide import PlotAide
from ginga.canvas.types import plots as gplots
from ginga.plot import time_series as tsp
from ginga.plot import data_source as dsp
from ginga.misc import Bunch

from qtpy import QtWidgets, QtCore, QtGui

import PlBase

# For "envmon3" plugin
al_envmon3 = dict(cat_rh = ['GEN2.CATWALK.NE.RHUMID',
                            'GEN2.CATWALK.SE.RHUMID',
                            'GEN2.CATWALK.SW.RHUMID',
                            'GEN2.CATWALK.NW.RHUMID'],
                  cat_temp = ['GEN2.CATWALK.NE.TEMPC',
                              'GEN2.CATWALK.SE.TEMPC',
                              'GEN2.CATWALK.SW.TEMPC',
                              'GEN2.CATWALK.NW.TEMPC'],
                  cat_dew = ['STATL.DEW_POINT_CATWALK_NE',
                             'STATL.DEW_POINT_CATWALK_SE',
                             'STATL.DEW_POINT_CATWALK_SW',
                             'STATL.DEW_POINT_CATWALK_NW',
                             'STATL.DEW_POINT_CATWALK.MEAN'],
                  misc = ['GEN2.CATWALK.TIME',
                          #'FITS.SBR.EPOCH',
                          ]
                  )


# starting dimensions of graph window (can change with window size)
dims = (600, 200)

# maximum number of data points to plot and save
# NOTE: currently catwalk data is collected only every 30 sec or so
catwalk_rate = 2 / 60.0
num_pts = int(24 * 60 * 60 * catwalk_rate)      # 24 hours worth

# interval (secs) between plot visual updates
# NOTE: this is independent of the rate at which data is saved
update_interval = 5.0

# interval (secs) between dataset flush to disk
save_interval = 10.0 * 60.0   # every 10 minutes

# initialize graphs to show back this time period from current time
show_last_time = 4.0 * 60 * 60

plot_colors = ['blue', 'palegreen4', 'darkviolet', 'brown', 'deeppink2']


class EnvMon3(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        #self.root.setStyleSheet("QWidget { background: lightblue }")

        #self.deques = {}
        self.alias_d = {}

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        container.setLayout(layout)

        lbl = QtWidgets.QLabel("Catwalk Sensors")
        lbl.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        lbl.setFont(QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold))
        layout.addWidget(lbl, stretch=0)

        self.plots = Bunch.Bunch()
        self.update_time = time.time()
        self.save_time = time.time()

        #y_rng = (-30.0, 50.0)
        names = ["NE", "SE", "SW", "NW"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon3['cat_temp'], num_pts,
                        y_acc=np.mean, title="Temp (C)")
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.catwalk_temp = res

        #y_rng = (0.0, 100.0)
        names = ["NE", "SE", "SW", "NW"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon3['cat_rh'], num_pts,
                        y_acc=np.mean, title="RH (%)",
                        warn_y=70, alert_y=80)
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.catwalk_rh = res

        #y_rng = (-30.0, 50.0)
        names = ["NE", "SE", "SW", "NW", "mean"]
        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_envmon3['cat_dew'], num_pts,
                        y_acc=np.mean, title="Dew Pt")
        layout.addWidget(res.widget.get_widget(), stretch=1)
        self.plots.catwalk_dew = res

        cross_connect_plots(self.plots.values())

        self.gui_up = True

    def start(self):
        aliases = []
        for name, _aliases in al_envmon3.items():
            aliases.extend(_aliases)

        self.save_file = os.path.join(os.environ['GEN2COMMON'], 'db',
                                      "statmon_envmon3.npy")
        try:
            d = np.load(self.save_file, allow_pickle=True)
            self.cst = dict(d[()])
        except Exception as e:
            self.logger.error("Couldn't open persist file: {}".format(e))
            self.cst = dict()

        t = time.time()

        for alias in aliases:

            if alias in self.alias_d:
                # create an array for this alias if we don't have one
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
        t = statusDict.get('GEN2.CATWALK.TIME', time.time())
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
        return 'envmon3'


def make_plot(alias_d, logger, dims, names, aliases, num_pts,
              y_acc=np.mean, title='',
              warn_y=None, alert_y=None,
              show_x_axis=True, show_y_axis=True):

    win_wd, win_ht = dims[:2]
    viewer = Viewers.CanvasView(logger, render='widget')

    viewer.set_desired_size(win_wd, win_ht)
    viewer.set_zoom_algorithm('rate')
    viewer.set_zoomrate(1.41)
    viewer.enable_autozoom('off')
    viewer.set_background('white')
    viewer.set_foreground('black')
    viewer.set_enter_focus(True)

    # our plot
    aide = PlotAide(viewer)
    aide.settings.set(autoaxis_x='pan', autoaxis_y='vis')

    bg = tsp.TimePlotBG(warn_y=warn_y, alert_y=alert_y, linewidth=2)
    aide.add_plot_decor(bg)

    title = tsp.TimePlotTitle(title=title)
    aide.add_plot_decor(title)

    x_axis = tsp.XTimeAxis(num_labels=4)
    aide.add_plot_decor(x_axis)

    y_axis = gplots.YAxis(num_labels=4)
    aide.add_plot_decor(y_axis)

    srcs = []
    for i, name in enumerate(names):
        psrc = gplots.XYPlot(name=name,
                             color=plot_colors[i % len(plot_colors)],
                             x_acc=np.mean, y_acc=y_acc,
                             linewidth=2.0, coord='data')
        aide.add_plot(psrc)

        buf = np.zeros((num_pts, 2), dtype=float)
        dsrc = dsp.XYDataSource(buf, overwrite=True, none_for_empty=True)
        dsrc.plot = psrc
        srcs.append(dsrc)

        alias = aliases[i]
        alias_d[alias] = Bunch.Bunch(plot=psrc, dsrc=dsrc, aide=aide)

    # add scrollbar interface around this viewer
    sw = Viewers.GingaScrolledViewerWidget(viewer=viewer, width=win_wd,
                                           height=win_ht)
    aide.configure_scrollbars(sw)

    res = Bunch.Bunch(viewer=viewer, aide=aide, sources=srcs, aliases=aliases,
                      widget=sw)
    return res

def cross_connect_plots(plot_info):
    # cross connect the plots so that zooming or panning in X in one
    # does the same to all the others
    plot_info = list(plot_info)
    m_settings = plot_info[0].aide.settings
    for res_a in plot_info:
        for res_b in set(plot_info) - set([res_a]):
            res_a.aide.add_callback('plot-zoom-x', res_b.aide.plot_zoom_x_cb)

        if res_a.aide.settings is not m_settings:
            m_settings.share_settings(res_a.aide.settings,
                                      keylist=['autoaxis_x'])
