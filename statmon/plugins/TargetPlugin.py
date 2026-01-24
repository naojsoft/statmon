#
# TargetPlugin.py -- miscellaneous table plugin for StatMon
#
# T. Inagaki
# E. Jeschke
#
import math

from ginga.gw import Widgets, GwHelp
from ginga.misc import Bunch

from g2cam.INS import INSdata
from g2cam.status.common import STATNONE, STATERROR
ERROR = ["Unknown", None, STATNONE, STATERROR, 'None']

import PlBase

clr_status = dict(off='white', normal='forestgreen', warning='orange', alarm='red')


class TargetPlugin(PlBase.Plugin):
    """ Target """

    def __set_aliases(self, inscode):

        self.aliases = ['FITS.{0}.PROP_ID'.format(inscode),
                        'FITS.{0}.OBJECT'.format(inscode),
                        'TSCL.INSROTPA_PF', 'STATS.ROTDIF_PF',
                        'TSCL.ImgRotPA', 'STATS.ROTDIF',
                        'TSCL.InsRotPA', 'TSCL.LIMIT_FLAG',
                        'TSCL.LIMIT_AZ', 'TSCL.LIMIT_EL_LOW',
                        'TSCL.LIMIT_EL_HIGH', 'TSCL.LIMIT_ROT',
                        'TSCV.PROBE_LINK', 'TSCV.FOCUSINFO',
                        'TSCV.FOCUSINFO2', 'TSCS.EL',
                        'STATS.SLEWING_TIME', 'STATS.SLEWING_STATUS',
                        'FITS.SBR.MAINOBCP',
                        ]
        self.logger.debug('setting aliases=%s' % self.aliases)

        self.controller.register_select('target', self.update, self.aliases)

    def set_layout(self, obcp):
        ins = INSdata()
        self.inscode = ins.getCodeByName(obcp)
        self.__set_aliases(self.inscode)

    def change_config(self, controller, d):
        obcp = d['inst']
        if obcp.startswith('#'):
            self.logger.debug(f'obcp is not assigned. {obcp}')
            return

        self.logger.debug(f"target changing config dict={str(d)} ins={d['inst']}")
        self.set_layout(obcp)

    def build_gui(self, container):

        self.font = GwHelp.get_font("Sans Bold", 11)

        self.w = Bunch.Bunch()
        self.inscode = 'SUK'

        gbox = Widgets.GridBox(rows=8, columns=4)
        gbox.set_border_width(2)
        gbox.set_row_spacing(2)
        gbox.add_widget(self._get_label("Proposal ID:"), 0, 0)
        self.w.propid = self._get_label("", halign='left')
        gbox.add_widget(self.w.propid, 0, 1)

        gbox.add_widget(self._get_label("Instrument:"), 1, 0)
        self.w.insname = self._get_label("", halign='left')
        gbox.add_widget(self.w.insname, 1, 1)

        gbox.add_widget(self._get_label("Object:"), 2, 0)
        self.w.object = self._get_label("", halign='left')
        gbox.add_widget(self.w.object, 2, 1)

        gbox.add_widget(self._get_label("Position Angle:"), 3, 0)
        self.w.pa = self._get_label("", halign='left')
        gbox.add_widget(self.w.pa, 3, 1)

        gbox.add_widget(self._get_label("Time to AZ Limit:"), 4, 0)
        self.w.tt_az_limit = self._get_label("", halign='left')
        gbox.add_widget(self.w.tt_az_limit, 4, 1)

        gbox.add_widget(self._get_label("Time to EL Limit:"), 5, 0)
        self.w.tt_el_limit = self._get_label("", halign='left')
        gbox.add_widget(self.w.tt_el_limit, 5, 1)

        gbox.add_widget(self._get_label("Time to ROT Limit:"), 6, 0)
        self.w.tt_rot_limit = self._get_label("", halign='left')
        gbox.add_widget(self.w.tt_rot_limit, 6, 1)

        gbox.add_widget(self._get_label("Slew Time:"), 7, 0)
        self.w.slew_time = self._get_label("", halign='left')
        gbox.add_widget(self.w.slew_time, 7, 1)

        container.add_widget(gbox, stretch=0)

        try:
            obcp = self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
            self.set_layout(obcp)
        except Exception as e:
            self.logger.error(f"error: building layout: {e}")

    def start(self):
        self.controller.register_select('target', self.update,
                                        self.aliases)
        self.controller.add_callback('change-config', self.change_config)

    def _get_label(self, name, halign=None):
        lbl = Widgets.Label(name, halign=halign)
        lbl.set_font(self.font)
        lbl.set_color(fg=clr_status['normal'])
        return lbl

    def update(self, status_dct):
        self.logger.debug('status=%s' % str(status_dct))
        try:
            self.update_info(status_dct)

        except Exception as e:
            self.logger.error(f"error: updating status: {e}")

    def update_info(self, status_dct):

        try:
            propid_alias = 'FITS.{0}.PROP_ID'.format(self.inscode)
            propid = status_dct.get(propid_alias, '#')
            color = clr_status['alarm'] if propid.startswith('#') else \
                clr_status['normal']
            self.w.propid.set_text(propid)
            self.w.propid.set_color(fg=color)

            insname_alias = 'FITS.SBR.MAINOBCP'
            self.w.insname.set_text(status_dct.get(insname_alias, '#'))

            object_alias = 'FITS.{0}.OBJECT'.format(self.inscode)
            self.w.object.set_text(status_dct.get(object_alias, 'None'))

            pa_alias, cmd_diff_alias = self.get_pa_status()
            self.update_pa(pa=status_dct.get(pa_alias),
                           cmd_diff=status_dct.get(cmd_diff_alias))

            self.update_azlimit(flag=status_dct.get('TSCL.LIMIT_FLAG'),
                                az=status_dct.get('TSCL.LIMIT_AZ'),)

            self.update_ellimit(flag=status_dct.get('TSCL.LIMIT_FLAG'),
                                low=status_dct.get('TSCL.LIMIT_EL_LOW'),
                                high=status_dct.get('TSCL.LIMIT_EL_HIGH'))

            self.update_rotlimit(flag=status_dct.get('TSCL.LIMIT_FLAG'),
                                 rot=status_dct.get('TSCL.LIMIT_ROT'),
                                 link=status_dct.get('TSCV.PROBE_LINK'),
                                 focus=status_dct.get('TSCV.FOCUSINFO'),
                                 focus2=status_dct.get('TSCV.FOCUSINFO2'))

            if status_dct['STATS.SLEWING_STATUS'] == 'NO':
                self.w.slew_time.set_text("(Not Slewing)")
                return

            time_sec = status_dct['STATS.SLEWING_TIME']
            if isinstance(time_sec, float):
                mn, sec = divmod(time_sec, 60)
                hr, mn = divmod(mn, 60)
                hr, mn, sec = int(hr), int(mn), int(sec)
                self.w.slew_time.set_text(f"{hr:02d}:{mn:02d}:{sec:02d}")
            else:
                self.w.slew_time.set_text(f"ERROR")

        except Exception as e:
            self.logger.error(f'error: target update: {e}')

    def get_pa_status(self):

        # TODO: redo this in Derive.py (status)
        if self.inscode in ['HSC', 'PFS']:
            # PF
            return ('TSCL.INSROTPA_PF', 'STATS.ROTDIF_PF')
        elif self.inscode in ['FCS', 'MCS', 'SWS', 'MMZ', 'COM']:
            # Cass
            return ('TSCL.InsRotPA', 'STATS.ROTDIF')
        else:
            # NS_IR and NS_OPT instruments
            return ('TSCL.ImgRotPA', 'STATS.ROTDIF')

    def update_pa(self, pa, cmd_diff):
        ''' pa = TSCL.INSROTPA_PF # POPT
            pa = TSCL.InsRotPA  # CS
            pa = TSCL.ImgRotPA  # NS
            cmd_diff = STATS.ROTDIF_PF # POPT
            cmd_diff = STATS.ROTDIF # CS/NS
        '''

        try:
            pa = ((pa + 540.0) % 360.0) - 180.0
        except Exception as e:
            self.logger.debug(f'error: pa calc. {e}')
            pa = None

        try:
            cmd_diff = math.fabs(float(cmd_diff))
        except Exception as e:
            cmd_diff = None
            self.logger.debug(f'error: cmd_diff to float. {e}')

        diff = 0.1
        color = clr_status['normal']

        if not (pa in ERROR or cmd_diff in ERROR):
            text = '{0:.2f} deg'.format(pa)
            if cmd_diff >= diff:
                color = clr_status['warning']
                #text = '{0:.2f} deg.  cmd_diff={1:.2f}>={2}'.format(pa, cmd_diff, diff)
                text = '{0:.2f} deg  Diff:{1:.2f}'.format(pa, cmd_diff)
        else:
            text = 'Undefined'
            color = clr_status['alarm']
            self.logger.error(f'error: pa={pa}, cmd_diff={cmd_diff}')

        self.w.pa.set_text(text)
        self.w.pa.set_color(fg=color)

    def update_azlimit(self, flag, az):
        ''' flag = TSCL.LIMIT_FLAG
            az = TSCL.LIMIT_AZ
        '''

        self.logger.debug(f'flag={flag}, az={az}')
        limit_flag = 0x04

        limit = 721 # in minute
        color = clr_status['normal']

        if flag in ERROR or az in ERROR:
            text = 'Undefined'
            color = clr_status['alarm']
        else:
            if flag & limit_flag:
                if az < limit:
                    #az_txt = "(Limit Az)"
                    limit = az

            if limit > 720.0: # plenty of time. 12 hours
                text = '--h --m'
            elif limit <= 1: # 0 to 1 minute left
                color = self.alarm
                hm  = to_hour_min(limit)
                text = '%s <= 1m' %(hm)
            elif limit > 30: # 30 to 720 min left
                hm = to_hour_min(limit)
                text = '%s' %(hm)
            else: # 1 to 30 min left
                color = clr_status['warning']
                hm = to_hour_min(limit)
                text = '%s <= 30m' %(hm)

        self.w.tt_az_limit.set_text(text)
        self.w.tt_az_limit.set_color(fg=color)

    def update_ellimit(self, flag, low, high):
        ''' flag = TSCL.LIMIT_FLAG
            low = TSCL.LIMIT_EL_LOW
            high = TSCL.LIMIT_EL_HIGH '''

        self.logger.debug(f'flag={flag}, low={low}, high={high}')
        low_limit = 0x01
        high_limit = 0x02

        limit = 721 # in minute
        color = clr_status['normal']
        el_txt = ''

        if flag in ERROR or low in ERROR or high in ERROR:
            text = 'Undefined'
            color = clr_status['alarm']
        else:
            if flag & low_limit:
                #<-- low value has been calculated
                if flag & high_limit:
                    #<-- high value has ALSO been calculated
                    # need to figure out which one to report
                    if low < high and low < limit:
                        el_txt = "(Low)"
                        limit = low
                    elif high < limit:
                        el_txt = "(High)"
                        limit = high
                else:
                    if low < limit:
                        el_txt = "(Low)"
                        limit = low

            elif flag & high_limit:
                #<-- high value has been calculated
                if high < limit:
                    el_txt = "(High)"
                    limit = high

            if limit > 720.0: # plenty of time. 12 hours
                text = '--h --m'
            elif limit <= 1: # 0 to 1 minute left
                color = clr_status['alarm']
                hm  = to_hour_min(limit)
                text = '%s <= 1m %s' % (hm, el_txt)
            elif limit > 30: # 30 to 720 min left
                hm = to_hour_min(limit)
                text = '%s %s' % (hm, el_txt)
            else: # 1 to 30 min left
                color = clr_status['warning']
                hm = to_hour_min(limit)
                text = '%s <= 30m %s' % (hm, el_txt)

        self.w.tt_el_limit.set_text(text)
        self.w.tt_el_limit.set_color(fg=color)

    def update_rotlimit(self, flag, rot, link, focus, focus2):
        ''' flag = TSCL.LIMIT_FLAG
            rot = TSCL.LIMIT_ROT
            link = TSCV.PROBE_LINK
            focus = TSCV.FOCUSINFO
            focus2 = TSCV.FOCUSINFO2
        '''

        pf = (0x01000000, 0x02000000, (0x00000000, 0x08))
        # NOTE: fails to format if focus or focus2 is not an int
        self.logger.debug(f'flag={flag}, rot={rot}, link={link}, focus=0x{focus:x}, focus2=0x{focus2:x}')
        limit_flag_rot = 0x08
        limit_flag_bigrot = 0x10
        link_flag = 0x01

        limit = 721 # in minute
        color = clr_status['normal']
        rot_txt = ''

        if flag in ERROR or rot in ERROR or link in ERROR:
            text = 'Undefined'
            color = clr_status['alarm']
        else:
            if not (flag & limit_flag_bigrot) \
               and (flag & limit_flag_rot):
                if rot < limit:
                     limit = rot

            prime_focus = focus in pf or (focus,focus2) in pf
            if (link & link_flag) == link_flag and not prime_focus:
                rot_txt = '(Probe)'
            else:
                rot_txt = '(Rotator)'

            if limit > 720.0: # plenty of time. 12 hours
                text = '--h --m'
            elif limit <= 1: # 0 to 1 minute left
                color = clr_status['alarm']
                hm  = to_hour_min(limit)
                text = '%s <= 1m %s' %(hm, rot_txt)
            elif limit > 30: # 30 to 720 min left
                hm = to_hour_min(limit)
                text = '%s %s' %(hm, rot_txt)
            else: # 1 to 30 min left
                color = clr_status['warning']
                hm = to_hour_min(limit)
                text = '%s <= 30m %s' %(hm, rot_txt)

        self.w.tt_rot_limit.set_text(text)
        self.w.tt_rot_limit.set_color(fg=color)


def to_hour_min(limit):
    ''' convert to hour-min'''
    try:
        h = limit // 60
        m = limit % 60
    except Exception as e:
        self.logger.error(f'error: to hour min. {e}')
        hm = '--h --m calc error'
    else:
        hm = '%dh %dm' %(h,m)
    finally:
        return hm
