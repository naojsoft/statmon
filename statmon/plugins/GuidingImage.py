#
# GuidingImage.py -- Guiding Image plugin for StatMon
#
# E. Jeschke
#
import os
import time
import numpy as np

import ginga.toolkit as ginga_toolkit
from ginga.misc import Bunch
from ginga.gw import Widgets, Viewers
from ginga.plot.plotaide import PlotAide
from ginga.canvas.types import plots as gplots
from ginga.plot import time_series as tsp
from ginga.plot import data_source as dsp

import PlBase
from EnvMon3 import cross_connect_plots, make_plot

# For "guiding image" plugin
ag_bright = 'TSCL.AG1Intensity'
sv_bright = 'TSCL.SV1Intensity'
#fmos_bright = 'TSCL.AGFMOSIntensity'
ag_seeing = 'VGWD.FWHM.AG'
sv_seeing = 'VGWD.FWHM.SV'
#fmos_seeing = 'TSCL.AGFMOSStarSize'

scag_bright = 'TSCL.HSC.SCAG.Intensity'
scag_seeing = 'TSCL.HSC.SCAG.StarSize'
shag_bright = 'TSCL.HSC.SHAG.Intensity'
shag_seeing = 'TSCL.HSC.SHAG.StarSize'

pfsag_bright = 'TSCL.PFS.AG.Intensity'
pfsag_seeing = 'TSCL.PFS.AG.StarSize'

# For "guiding error" plot
ag_error_x = 'TSCL.AG1dX'
ag_error_y = 'TSCL.AG1dY'

sv_error_x = 'TSCL.SV1DX'
sv_error_y = 'TSCL.SV1DY'

hsc_error_x = 'TSCL.HSC.SCAG.DX'
hsc_error_y = 'TSCL.HSC.SCAG.DY'

pfs_error_x = 'TSCL.PFS.AG.DX'
pfs_error_y = 'TSCL.PFS.AG.DY'

al_guiding = [ag_error_x, ag_error_y,
              sv_error_x, sv_error_y,
              hsc_error_x, hsc_error_y,
              pfs_error_x, pfs_error_y,
              ag_bright, sv_bright,  #fmos_bright,
              ag_seeing, sv_seeing,  #fmos_seeing,
              scag_bright, scag_seeing,
              shag_bright, shag_seeing,
              'GEN2.STATUS.TBLTIME.TSCL',
              pfsag_bright, pfsag_seeing,
              ]

al_error = [ag_error_x, ag_error_y,
            sv_error_x, sv_error_y,
            hsc_error_x, hsc_error_y,
            pfs_error_x, pfs_error_y]

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

plot_colors = ['darkviolet', 'palegreen4']


class GuidingImage(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(2, 2, 2, 2)

        self.alias_d = {}
        self.plots = Bunch.Bunch()
        # self.cst = None
        self.update_time = time.time()
        self.save_time = time.time()

        self.sub_widget = None
        self.gui_up = True

    def configure_plots(self, obcp):

        self.alias_d = {}
        self.plots = Bunch.Bunch()

        # delete old widget
        w = self.sub_widget
        if w is not None:
            self.sub_widget = None
            self.root.remove(w)
            w.delete()

        names_err = ['X', 'Y']
        if obcp is None or obcp.startswith('#') or obcp in PlBase.ao_inst:
            self.logger.debug("OBCP ({}) is not a guiding instrument".format(obcp))
            return
        # NOTE: FMOS decommissioned...2021 EJ
        ## elif obcp == 'FMOS':
        ##     names = ['FMOS']
        ##     bright = [fmos_bright]
        ##     seeing = [fmos_seeing]
        elif obcp == 'HSC':
            names = ['SCAG', 'SHAG']
            al_error = [hsc_error_x, hsc_error_y]
            al_bright = [scag_bright, shag_bright]
            al_seeing = [scag_seeing, shag_seeing]
        elif obcp == 'PFS':
            names = ['PFSAG']
            al_error = [pfs_error_x, pfs_error_y]
            al_bright = [pfsag_bright]
            al_seeing = [pfsag_seeing]
        elif obcp == 'HDS':
            # NOTE: AG is not used with HDS any more...2021 EJ
            #names = ['AG', 'SV']
            #al_bright = [ag_bright, sv_bright]
            #al_seeing = [ag_seeing, sv_seeing]
            names = ['SV']
            al_error = [sv_error_x, sv_error_y]
            al_bright = [sv_bright]
            al_seeing = [sv_seeing]
        else:
            # other guiding instrument
            names = ['AG']
            al_error = [ag_error_x, ag_error_y]
            al_bright = [ag_bright]
            al_seeing = [ag_seeing]

        w = Widgets.VBox()
        self.sub_widget = w
        w.set_margins(0, 0, 0, 0)
        w.set_spacing(2)

        res = make_plot(self.alias_d, self.logger, dims,
                        names_err, al_error, num_pts,
                        y_acc=np.mean, title="Error")
        w.add_widget(res.widget, stretch=1)
        self.plots.guiding_error = res

        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_bright, num_pts,
                        y_acc=np.mean, title="Brightness")
        w.add_widget(res.widget, stretch=1)
        self.plots.brightness = res

        res = make_plot(self.alias_d, self.logger, dims,
                        names, al_seeing, num_pts,
                        y_acc=np.mean, title="Seeing",
                        warn_y=1.0)
        w.add_widget(res.widget, stretch=1)
        self.plots.seeing = res

        cross_connect_plots(self.plots.values())

        self.root.add_widget(w, stretch=1)

        # t = time.time()

        # for alias in self.alias_d.keys():
        #     points = self.cst[alias]
        #     bnch = self.alias_d[alias]
        #     bnch.dsrc.set_points(points)
        #     dsp.update_plot_from_source(bnch.dsrc, bnch.plot,
        #                                 update_limits=True)

        #     bnch.aide.zoom_limit_x(t - show_last_time, t)

        # self.update_plots()

    def start(self):
        aliases = al_guiding

        self.save_file = os.path.join(os.environ['GEN2COMMON'], 'db',
                                      "statmon_guidingimage.npy")
        try:
            d = np.load(self.save_file, allow_pickle=True)
            self.cst = dict(d[()])
        except Exception as e:
            self.logger.error("Couldn't open persist file: {}".format(e))
            self.cst = dict()

        t = time.time()

        # for alias in aliases:
        #     # create a chest item for this alias if we don't have one
        #     if alias not in self.cst:
        #         self.cst[alias] = np.zeros((0, 2), dtype=float)

        obcp = self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
        self.configure_plots(obcp)

        self.controller.register_select(str(self), self.update, aliases)
        self.controller.add_callback('change-config', self.change_config)

    def stop(self):
        #self.update_persist()
        pass

    def change_config(self, controller, d):
        """This get's called if we have a change in configuration
        (e.g. instrument changed)
        """
        obcp = d.get('inst', None)
        self.configure_plots(obcp)

    def update(self, statusDict):
        #print(statusDict)
        t = statusDict.get('GEN2.STATUS.TBLTIME.TSCL', time.time())
        #t = statusDict.get('FITS.SBR.EPOCH', time.time())
        self.logger.debug("status update t={}".format(t))

        try:
            for alias in self.alias_d.keys():

                if alias in statusDict:
                    val = statusDict[alias]
                    if isinstance(val, float):
                        if alias in al_error:
                            val *= 0.001
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

            # secs_since = t - self.save_time
            # self.logger.debug("{0:.2f} secs since last persist update".format(secs_since))
            # if t - self.save_time >= save_interval:
            #     self.update_persist()

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

    # def update_persist(self):
    #     t = time.time()
    #     self.save_time = t
    #     self.logger.debug('persisting data')
    #     # Ugh. It seems we have to reassign the arrays into the chest
    #     # every time, otherwise the additions to the array do not persist
    #     # in the chest when it is flushed
    #     # Double Ugh. Seems Chest does not have an update() method
    #     for alias, bnch in self.alias_d.items():
    #         self.cst[alias] = bnch.dsrc.get_points()

    #     try:
    #         np.save(self.save_file, self.cst, allow_pickle=True)
    #     except Exception as e:
    #         self.logger.error("Error saving array state: {}".format(e),
    #                           exc_info=True)
    #     t1 = time.time()
    #     self.logger.debug("time to persist data {0:.4f} sec".format(t1 - t))

    def __str__(self):
        return 'guidingimage'
