#
# RaDec.py -- RA/DEC plugin for StatMon
# 
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Fri Apr 27 17:57:38 HST 2012
#]
#
import time
import math
import astro.radec as radec
import astro.wcs as wcs

import PlBase
import Bunch

from PyQt4 import QtGui, QtCore
from Gen2.Fitsview.qtw import QtHelp

# For "RaDec" plugin
al_ra = 'FITS.SBR.RA'
al_ra_cmd = 'FITS.SBR.RA_CMD'
al_dec = 'FITS.SBR.DEC'
al_dec_cmd = 'FITS.SBR.DEC_CMD'
al_az = 'TSCS.AZ'
al_az_cmd = 'TSCS.AZ_CMD'
al_el = 'TSCS.EL'
al_el_cmd = 'TSCS.EL_CMD'
al_rot = 'FITS.SBR.INSROT'
al_rot_cmd = 'FITS.SBR.INSROT_CMD'

# For "Times" plugin
al_epoch = 'FITS.SBR.EPOCH'
al_ras = 'STATS.RA'
al_ut1utc = 'FITS.SBR.UT1_UTC'


class RaDec(PlBase.Plugin):

    def _build_cluster(self):
        vbox = QtHelp.VBox()
        layout = vbox.layout()
        lt = QtGui.QLabel()
        lt.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(lt, stretch=0, alignment=QtCore.Qt.AlignTop)
        lm = QtGui.QLabel()
        lm.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(lm, stretch=0, alignment=QtCore.Qt.AlignTop)
        lb = QtGui.QLabel()
        lb.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(lb, stretch=0, alignment=QtCore.Qt.AlignTop)

        return Bunch.Bunch(box=vbox, lt=lt, lm=lm, lb=lb)
        
    def build_gui(self, container):
        self.root = container
        self.root.setStyleSheet("QWidget { background: lightblue }")

        self.labels = (('ra', al_ra, al_ra_cmd), ('dec', al_dec, al_dec_cmd),
                       ('az', al_az, al_az_cmd), ('el', al_el, al_el_cmd),
                       ('rot', al_rot, al_rot_cmd),
                       )
        
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        container.setLayout(layout)

        #self.bigfont = QtGui.QFont("Arial Black", 28)
        self.bigfont = QtGui.QFont("Helvetica", 28, QtGui.QFont.Bold)
        self.midfont = QtGui.QFont("Helvetica", 18, QtGui.QFont.Bold)
        self.smfont = QtGui.QFont("Helvetica", 12, QtGui.QFont.Bold)

        self.w = Bunch.Bunch()

        bnch = self._build_cluster()
        bnch.lm.setFont(self.smfont)
        bnch.lm.setText("Current")
        bnch.lb.setFont(self.smfont)
        bnch.lb.setText("Commanded")
        bnch.lt.setFont(self.smfont)
        layout.addWidget(bnch.box, stretch=0)
        self.w['rowhdr'] = bnch

        for name, alias1, alias2 in self.labels:
            bnch = self._build_cluster()
            bnch.lm.setFont(self.bigfont)
            bnch.lm.setText(name)
            bnch.lb.setFont(self.midfont)
            bnch.lt.setFont(self.smfont)
            layout.addWidget(bnch.box, stretch=0)
            layout.addStretch(stretch=1)
            self.w[name] = bnch

        self.w.ra.lt.setText("RA (2000.0)")
        self.w.dec.lt.setText("DEC (2000.0)")
        self.w.az.lt.setText("Az (deg:S=0,W=90)")
        self.w.el.lt.setText("El (deg)")
        self.w.rot.lt.setText("Rot (deg)")

    def start(self):
        aliases = []
        for name, alias1, alias2 in self.labels:
            aliases.extend([alias1, alias2])
        self.controller.register_select('radec', self.update, aliases)

    def update(self, statusDict):
        self.w.ra.lm.setText(statusDict[al_ra])
        self.w.dec.lm.setText(statusDict[al_dec])
        self.w.ra.lb.setText(statusDict[al_ra_cmd])
        self.w.dec.lb.setText(statusDict[al_dec_cmd])

        # Azimuth, actual
        try:
            az = float(statusDict[al_az])
            # Mitsubishi says 
            az_str = "%+5.2f" % (az)
        except Exception, e:
            self.logger.error("Error displaying azimuth: %s" % (str(e)))
            az_str = "ERROR"
        self.w.az.lm.setText(az_str)

        # Azimuth, commanded
        try:
            az = float(statusDict[al_az_cmd])
            # Mitsubishi says 
            az_str = "%+5.2f" % (az)
        except Exception, e:
            self.logger.error("Error displaying azimuth: %s" % (str(e)))
            az_str = "ERROR"
        self.w.az.lb.setText(az_str)

        # Elevation, actual
        try:
            el_str = "%+5.2f" % (float(statusDict[al_el]))
        except Exception, e:
            self.logger.error("Error displaying elevation: %s" % (str(e)))
            el_str = "ERROR"
        self.w.el.lm.setText(el_str)

        # Elevation, commanded
        try:
            el_str = "%+5.2f" % (float(statusDict[al_el_cmd]))
        except Exception, e:
            self.logger.error("Error displaying elevation: %s" % (str(e)))
            el_str = "ERROR"
        self.w.el.lb.setText(el_str)

        # Rotator, actual
        try:
            rot_str = "%+5.2f" % (float(statusDict[al_rot]))
        except Exception, e:
            self.logger.error("Error displaying rotation: %s" % (str(e)))
            rot_str = "ERROR"
        self.w.rot.lm.setText(rot_str)

        # Rotator, commanded
        try:
            rot_str = "%+5.2f" % (float(statusDict[al_rot_cmd]))
        except Exception, e:
            self.logger.error("Error displaying rotation: %s" % (str(e)))
            rot_str = "ERROR"
        self.w.rot.lb.setText(rot_str)
        
    
    def __str__(self):
        return 'radec'

    
class Times(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        self.root.setStyleSheet("QWidget { background: lightblue }")

        self.labels = [ 'ut', 'hst', 'lst', 'ha' ]

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        container.setLayout(layout)
        
        self.bigfont = QtGui.QFont("Arial Black", 24)

        self.w = Bunch.Bunch()

        layout.addStretch(stretch=1)
        for name in self.labels:
            w = QtGui.QLabel()
            w.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            w.setFont(self.bigfont)
            layout.addWidget(w, stretch=0, alignment=QtCore.Qt.AlignCenter)
            layout.addStretch(stretch=1)
            self.w[name] = w

    def start(self):
        aliases = [al_ut1utc, al_ras, al_epoch]
        self.controller.register_select('times', self.update, aliases)

    def update(self, statusDict):
        t_sec = statusDict[al_epoch]
        ut1_utc = statusDict[al_ut1utc]

        hst = time.strftime('%H:%M:%S (%b/%d)', time.localtime(t_sec))
        ut = time.strftime('%H:%M:%S (%b/%d)', time.gmtime(t_sec))
        lst_sec = wcs.calcLST_sec(t_sec, ut1_utc)
        lst_tup = wcs.adjustTime(lst_sec, 0)
        lst = '%02d:%02d:%02d' % lst_tup[3:6]

        ra_deg = radec.funkyHMStoDeg(statusDict[al_ras])
        ha_sec = wcs.calcHA_sec(lst_sec, ra_deg)
        ha_abs = math.fabs(ha_sec)
        ha_hrs = ha_abs // 3600
        ha_abs -= ha_hrs
        ha_min = ha_abs // 60
        ha_sec = ha_abs - ha_min
        c = '+'
        if ha_sec < 0.0:
            c = '-'
        # TODO
        ha = '%s%02dh:%02dm' % (c, ha_hrs, ha_min)

        self.w.ut.setText("UT: %s" % ut)
        self.w.hst.setText("HST: %s" % hst)
        self.w.lst.setText("LST: %s" % lst)
        self.w.ha.setText("HA: %s" % ha)
    
    def __str__(self):
        return 'times'
    
#END
