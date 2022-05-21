#
# GuidingError.py -- Guiding error 2D XY scatter plot plugin for StatMon
#
# E. Jeschke
#
import os
import time
import numpy as np

from qtpy import QtWidgets

from ginga.gw import Widgets
from ginga.plot.xy_scatter import TimedXYScatterPlot

import PlBase

is_simulation = False

# PFS auto guiding status aliases
aliases = ['STATL.TELDRIVE', 'GEN2.STATUS.TBLTIME.TSCL',
           'FITS.SBR.MAINOBCP',
           # for PFS
           'TSCL.PFS.AG.DX', 'TSCL.PFS.AG.DY',
           'TSCL.PFS.AG.dAZ', 'TSCL.PFS.AG.dEL',
           'TSCL.PFS.AG.Intensity', 'TSCL.PFS.AG.StarSize',
           'TSCV.PFS.AG.ExpTime', 'TSCV.PFS.AG.CCalc',
           'TSCV.PFS.AG.AutoGuideReady', 'TSCV.PFS.AG.CamIFAlarm',
           'TSCV.PFS.AG.IFAlarms', 'TSCV.PFS.AG.MLP1IFAlarm',
           # for HSC
           'TSCL.HSC.SCAG.DX', 'TSCL.HSC.SCAG.DY',
           # for HDS
           'TSCL.SV1DX', 'TSCL.SV1DY',
           # all telescope AG guiders
           'TSCL.AG1dX', 'TSCL.AG1dY',
           ]

# starting dimensions of graph window (can change with window size)
dims = (500, 500)

# interval (secs) between plot visual updates
# NOTE: this is independent of the rate at which data is saved
update_interval = 2.0


class GuidingError(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container

        self.stat_d = {}

        self.guiding = False
        self.tel_mode = ""
        self.err_pt = (None, None)
        self.auto_clear = False
        self.update_time = time.time()

        # scale factor for adjusting PFS error values received
        # from the telescope to convert to arcsec
        self.scale_factor = 0.001

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        container.setLayout(layout)

        vbox = Widgets.VBox()
        top = Widgets.VBox()
        plot = TimedXYScatterPlot(self.logger)
        plot.build_gui(vbox)
        self.plot = plot

        top.add_widget(vbox, stretch=1)

        hbox = Widgets.HBox()
        btn = Widgets.Button('Clear')
        btn.add_callback('activated', lambda w: plot.clear_plot())
        btn.set_tooltip("Clear all points from the plot")
        hbox.add_widget(btn, stretch=0)

        ent = Widgets.SpinBox(dtype=float)
        ent.set_limits(1.0, 60.0, incr_value=1.0)
        ent.set_value(plot.range_t / 60.0)
        ent.set_tooltip("Set minute range for plot")
        ent.add_callback('value-changed', lambda w, val: plot.set_range(val * 60))
        hbox.add_widget(ent, stretch=0)

        ent = Widgets.TextEntrySet()
        ent.set_text(str(plot.num_pts))
        ent.set_tooltip("Set maximum number of points in plot")
        ent.add_callback('activated', lambda w: plot.set_num_pts(int(w.get_text())))
        hbox.add_widget(ent, stretch=0)

        cbox = Widgets.ComboBox()
        for text in plot.styles:
            cbox.append_text(text)
        cbox.set_tooltip("Set plot point style")
        cbox.set_text(plot.style)
        cbox.add_callback('activated', lambda w, idx: plot.set_style(w.get_text()))
        hbox.add_widget(cbox, stretch=0)

        cbox = Widgets.CheckBox("Auto clear")
        cbox.set_state(self.auto_clear)
        cbox.set_tooltip("Clear plot when guiding restarts")
        cbox.add_callback('activated', lambda w, tf: self.auto_clear_cb(tf))
        hbox.add_widget(cbox, stretch=0)
        hbox.add_widget(Widgets.Label(''), stretch=1)

        top.add_widget(hbox, stretch=0)
        #top.resize(500, 600)
        w = top.get_widget()

        layout.addWidget(w, stretch=1)

        self.gui_up = True

    def start(self):
        self.controller.register_select(str(self), self.update, aliases)

    def update(self, statusDict):
        t = statusDict.get('GEN2.STATUS.TBLTIME.TSCL', time.time())
        #t = statusDict.get('FITS.SBR.EPOCH', time.time())
        self.logger.debug("status update t={}".format(t))

        try:
            self.stat_d.update({key: statusDict[key]
                                for key in aliases if key in statusDict})

            t = time.time()
            secs_since = t - self.update_time
            self.logger.debug("{0:.2f} secs since last plot update".format(secs_since))
            if secs_since >= update_interval:
                self.update_plot()

        except Exception as e:
            self.logger.error("error updating from status: {}".format(e),
                              exc_info=True)

    def get_errpt(self, d):
        ins = d.get('FITS.SBR.MAINOBCP', 'SUKA').strip()
        if ins == 'PFS':
            err_pt = (d['TSCL.PFS.AG.DX'], d['TSCL.PFS.AG.DY'])
        elif ins == 'HSC':
            err_pt = (d['TSCL.HSC.SCAG.DX'], d['TSCL.HSC.SCAG.DY'])
        elif ins == 'HDS':
            err_pt = (d['TSCL.SV1DX'], d['TSCL.SV1DY'])
        elif ins in ['FOCAS', 'MOIRCS', 'SWIMS', 'COMICS', 'SUKA']:
            err_pt = (d['TSCL.AG1dX'], d['TSCL.AG1dY'])
        else:
            return None

        # NOTE: required because of telescope side encoding?
        err_pt = np.array(err_pt) * self.scale_factor
        dx, dy = err_pt
        return (dx, dy)

    def update_plot(self):
        t = time.time()
        self.update_time = t
        self.logger.debug('updating plot')
        d = self.stat_d.copy()
        self.logger.debug("status: {}".format(str(d)))
        tel_mode = d['STATL.TELDRIVE']
        if tel_mode.startswith('Guiding'):
            if tel_mode != self.tel_mode:
                self.tel_mode = tel_mode
                self.plot.set_title_msg(tel_mode, color='green4')

            if not self.guiding:
                self.guiding = True
                if self.auto_clear:
                    self.plot.clear_plot()

            err_pt = self.get_errpt(d)
            if err_pt != self.err_pt:
                self.err_pt = err_pt
                if err_pt is not None:
                    self.plot.plot_point(err_pt, t)

        else:
            if tel_mode != self.tel_mode:
                self.tel_mode = tel_mode
                self.plot.set_title_msg(tel_mode)
            if self.guiding:
                self.guiding = False
        t1 = time.time()
        self.logger.debug("time to update plots {0:.4f} sec".format(t1 - t))

    def auto_clear_cb(self, tf):
        self.auto_clear = tf

    def __str__(self):
        return 'guidingerror'
