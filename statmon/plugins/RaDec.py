#
# RaDec.py -- RA/DEC plugin for StatMon
#
# E. Jeschke
#
import time
import math
from datetime import datetime
from dateutil import tz

import g2base.astro.radec as radec
import g2base.astro.wcs as wcs

from ginga.gw import Widgets, GwHelp
from ginga.misc import Bunch

import PlBase

# For "RaDec" plugin
al_ra = 'FITS.SBR.RA'
al_ra_cmd = 'FITS.SBR.RA_CMD'
al_dec = 'FITS.SBR.DEC'
al_dec_cmd = 'FITS.SBR.DEC_CMD'
al_az = 'TSCS.AZ'
#al_az_cmd = 'TSCS.AZ_CMD'
al_az_cmd = 'STATS.AZ_CMD'
al_el = 'TSCS.EL'
#al_el_cmd = 'TSCS.EL_CMD'
al_el_cmd = 'STATS.EL_CMD'
al_rot = 'FITS.SBR.INSROT'
al_rot_cmd = 'FITS.SBR.INSROT_CMD'
al_airmass = 'TSCS.EL'
al_airmass_cmd = 'TSCS.EL'

# For "Times" plugin
al_epoch = 'FITS.SBR.EPOCH'
al_ras = 'STATS.RA'
al_ut1utc = 'FITS.SBR.UT1_UTC'


class RaDec(PlBase.Plugin):

    def _build_cluster(self):
        vbox = Widgets.VBox()
        lt = Widgets.Label()
        lt.set_halign('center')
        vbox.add_widget(lt, stretch=0)
        lm = Widgets.Label()
        lm.set_halign('center')
        vbox.add_widget(lm, stretch=0)
        lb = Widgets.Label()
        lb.set_halign('center')
        vbox.add_widget(lb, stretch=0)

        return Bunch.Bunch(box=vbox, lt=lt, lm=lm, lb=lb)

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)
        #self.root.get_widget().setStyleSheet("QWidget { background: lightblue }")

        self.labels = (('ra', al_ra, al_ra_cmd), ('dec', al_dec, al_dec_cmd),
                       ('az', al_az, al_az_cmd), ('el', al_el, al_el_cmd),
                       ('rot', al_rot, al_rot_cmd), ('airmass', al_el, al_el))

        hbox = Widgets.HBox()
        hbox.set_margins(4, 4, 4, 4)
        hbox.set_spacing(2)
        hbox.set_expanding(True, False)
        self.root.add_widget(hbox, stretch=0)

        #fontfamily = "DejaVu Sans Mono Bold"
        fontfamily = "Monospace Bold"
        self.biggerfont = (fontfamily, 36)
        self.bigfont = (fontfamily, 28)
        self.midfont = (fontfamily, 18)
        self.smfont = (fontfamily, 12)

        self.w = Bunch.Bunch()

        bnch = self._build_cluster()
        bnch.lm.set_font(*self.smfont)
        bnch.lm.set_text("Current")
        bnch.lb.set_font(*self.smfont)
        bnch.lb.set_text("Commanded")
        bnch.lt.set_font(*self.smfont)
        hbox.add_widget(bnch.box, stretch=0)
        self.w['rowhdr'] = bnch

        for name, alias1, alias2 in self.labels:
            bnch = self._build_cluster()
            bnch.lm.set_font(*self.bigfont)
            if name == 'airmass':
                bnch.lm.set_font(*self.biggerfont)
                bnch.lm.set_text(name)
            else:
                bnch.lm.set_text(name)
                bnch.lb.set_font(*self.midfont)
            bnch.lt.set_font(*self.smfont)
            hbox.add_widget(bnch.box, stretch=0)
            #hbox.get_widget().layout().addStretch(stretch=1)
            self.w[name] = bnch

        self.w.ra.lt.set_text("RA (2000.0)")
        self.w.dec.lt.set_text("DEC (2000.0)")
        self.w.az.lt.set_text("Az (deg:S=0,W=90)")
        self.w.el.lt.set_text("El (deg)")
        self.w.rot.lt.set_text("Rot (deg)")
        self.w.airmass.lt.set_text('AirMass')

    def start(self):
        aliases = []
        for name, alias1, alias2 in self.labels:
            aliases.extend([alias1, alias2])
        self.controller.register_select('radec', self.update, aliases)

    def update(self, statusDict):
        self.w.ra.lm.set_text(statusDict[al_ra])
        self.w.dec.lm.set_text(statusDict[al_dec])
        self.w.ra.lb.set_text(statusDict[al_ra_cmd])
        self.w.dec.lb.set_text(statusDict[al_dec_cmd])

        # Airmass calculation
        try:
            el = float(statusDict[al_el])
            assert 1.0 <= el <=179.0
        except Exception as e:
            self.logger.error("Error displaying airmass: %s" % (str(e)))
            airmass_str = "ERROR"
        else:
            zd = 90.0 - el
            rad = math.radians(zd)
            sz = 1.0 / math.cos(rad)
            sz1 = sz - 1.0
            am = sz - 0.0018167 * sz1 - 0.002875 * sz1**2 - 0.0008083 * sz1**3
            airmass_str = '{0:.3f}'.format(am)
        finally:
            self.w.airmass.lm.set_text(airmass_str)

        # Azimuth, actual
        try:
            az = float(statusDict[al_az])
            # Mitsubishi says
            az_str = "%+5.2f" % (az)
        except Exception as e:
            self.logger.error("Error displaying azimuth: %s" % (str(e)))
            az_str = "ERROR"
        self.w.az.lm.set_text(az_str)

        # Azimuth, commanded
        try:
            az = float(statusDict[al_az_cmd])
            # Mitsubishi says
            az_str = "%+5.2f" % (az)
        except Exception as e:
            self.logger.error("Error displaying azimuth: %s" % (str(e)))
            az_str = "ERROR"
        self.w.az.lb.set_text(az_str)

        # Elevation, actual
        try:
            el_str = "%+5.2f" % (float(statusDict[al_el]))
        except Exception as e:
            self.logger.error("Error displaying elevation: %s" % (str(e)))
            el_str = "ERROR"
        self.w.el.lm.set_text(el_str)

        # Elevation, commanded
        try:
            el_str = "%+5.2f" % (float(statusDict[al_el_cmd]))
        except Exception as e:
            self.logger.error("Error displaying elevation: %s" % (str(e)))
            el_str = "ERROR"
        self.w.el.lb.set_text(el_str)

        # Rotator, actual
        try:
            rot_str = "%+5.2f" % (float(statusDict[al_rot]))
        except Exception as e:
            self.logger.error("Error displaying rotation: %s" % (str(e)))
            rot_str = "ERROR"
        self.w.rot.lm.set_text(rot_str)

        # Rotator, commanded
        try:
            rot_str = "%+5.2f" % (float(statusDict[al_rot_cmd]))
        except Exception as e:
            self.logger.error("Error displaying rotation: %s" % (str(e)))
            rot_str = "ERROR"
        self.w.rot.lb.set_text(rot_str)


    def __str__(self):
        return 'radec'


class Times(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)
        #self.root.get_widget().setStyleSheet("QWidget { background: lightblue }")

        self.labels = [ 'ut', 'hst', 'lst', 'ha' ]
        self.hst_tz = tz.gettz('US/Hawaii')

        hbox = Widgets.HBox()
        hbox.set_margins(4, 4, 4, 4)
        hbox.set_spacing(2)
        hbox.set_expanding(True, False)
        self.root.add_widget(hbox, stretch=0)

        fontfamily = "Monospace"
        self.bigfont = (fontfamily, 24)

        self.w = Bunch.Bunch()

        # layout = hbox.get_widget().layout()
        # layout.addStretch(stretch=1)
        for name in self.labels:
            w = Widgets.Label()
            w.set_halign('center')
            w.set_font(*self.bigfont)
            hbox.add_widget(w, stretch=0)
            #layout.addStretch(stretch=1)
            self.w[name] = w

    def start(self):
        aliases = [al_ut1utc, al_ras, al_epoch]
        self.controller.register_select('times', self.update, aliases)

    def update(self, statusDict):
        t_sec = statusDict[al_epoch]
        ut1_utc = statusDict[al_ut1utc]
        self.logger.debug("epoch: {}  ut1-utc: {}".format(t_sec, ut1_utc))

        try:
            # Display HST even in Mitaka, Japan
            fmt = '%H:%M:%S (%b/%d)'
            hst_time = datetime.fromtimestamp(t_sec, tz=tz.UTC).astimezone(self.hst_tz)
            hst = hst_time.strftime(fmt)
            ut = time.strftime(fmt, time.gmtime(t_sec))

            lst_sec = wcs.calcLST_sec(t_sec, ut1_utc)
            lst_tup = wcs.adjustTime(lst_sec, 0)
            lst = '%02d:%02d:%02d' % lst_tup[3:6]

            ra_deg = radec.funkyHMStoDeg(statusDict[al_ras])
            ha_sec = wcs.calcHA_sec(lst_sec, ra_deg)
            c = '+'
            if ha_sec < 0.0:
                c = '-'
            ha_abs = math.fabs(ha_sec)
            ha_hrs = ha_abs // 3600
            ha_abs -= (ha_hrs * 3600)
            ha_min = ha_abs // 60
            ha_sec = ha_abs - (ha_min * 60)
            # TODO
            ha = '%s%02dh:%02dm' % (c, ha_hrs, ha_min)

            self.w.ut.set_text("UT: %s" % ut)
            self.w.hst.set_text("HST: %s" % hst)
            self.w.lst.set_text("LST: %s" % lst)
            self.w.ha.set_text("HA: %s" % ha)

        except Exception as e:
            self.logger.error("Error updating times: {}".format(str(e)))

    def __str__(self):
        return 'times'

#END
