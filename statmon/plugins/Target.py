#
# T. Inagaki
#
from ginga.gw import Widgets

from Propid import PropIdDisplay
from InsName import InsNameDisplay
from Object import ObjectDisplay
from Airmass import AirmassDisplay
from Pa import PaDisplay
from TimeAz import TimeAzLimitDisplay
from TimeEl import TimeElLimitDisplay
from TimeRot import TimeRotLimitDisplay


class TargetGui(Widgets.VBox):
    def __init__(self, parent=None, obcp=None, logger=None):
        super().__init__()
        self.set_spacing(1)
        self.set_margins(0, 0, 0, 0)

        self.obcp = obcp  # instrument 3 letter code
        self.logger = logger
        self.propid = PropIdDisplay(logger=logger)
        self.insname = InsNameDisplay(logger=logger)
        self.object = ObjectDisplay(logger=logger)
        #self.airmass = AirmassDisplay(logger=logger)
        self.pa = PaDisplay(logger=logger)
        self.time_az = TimeAzLimitDisplay(logger=logger)
        self.time_el = TimeElLimitDisplay(logger=logger)
        self.time_rot = TimeRotLimitDisplay(logger=logger)
        self.set_layout()

    def set_layout(self):
        self.add_widget(self.propid)
        self.add_widget(self.insname)
        self.add_widget(self.object)
        #self.add_widget(self.airmass)
        self.add_widget(self.pa)
        self.add_widget(self.time_az)
        self.add_widget(self.time_el)
        self.add_widget(self.time_rot)


class Target(TargetGui):
    def __init__(self, parent=None, obcp=None, logger=None):
        super(Target, self).__init__(parent=parent, obcp=obcp, logger=logger)

    def get_pa_status(self):

        # TODO: redo this in Derive.py (status)
        if self.obcp in ['HSC', 'PFS']:
            # PF
            return ('TSCL.INSROTPA_PF', 'STATS.ROTDIF_PF')
        elif self.obcp in ['FCS', 'MCS', 'SWS', 'MMZ', 'COM']:
            # Cass
            return ('TSCL.InsRotPA', 'STATS.ROTDIF')
        else:
            # NS_IR and NS_OPT instruments
            return ('TSCL.ImgRotPA', 'STATS.ROTDIF')

    def update_target(self, **kargs):

        self.logger.debug(f'updating telescope. kargs={kargs}')

        try:
            propid = 'FITS.{0}.PROP_ID'.format(self.obcp)
            self.propid.update_propid(propid=kargs.get(propid))

            insname = 'FITS.SBR.MAINOBCP'
            self.insname.update_insname(insname=kargs.get(insname))

            obj = 'FITS.{0}.OBJECT'.format(self.obcp)
            self.object.update_object(obj=kargs.get(obj))

            #self.airmass.update_airmass(el=kargs.get('TSCS.EL'))

            # pa = TSCL.INSROTPA_PF | TSCL.InsRotPA | TSCL.ImgRotPA
            # cmd_diff = STATS.ROTDIF_PF | STATS.ROTDIF
            pa, cmd_diff = self.get_pa_status()
            self.pa.update_pa(pa=kargs.get(pa),
                              cmd_diff=kargs.get(cmd_diff))

            self.time_az.update_azlimit(flag=kargs.get('TSCL.LIMIT_FLAG'),
                                        az=kargs.get('TSCL.LIMIT_AZ'),)

            self.time_el.update_ellimit(flag=kargs.get('TSCL.LIMIT_FLAG'),
                                        low=kargs.get('TSCL.LIMIT_EL_LOW'),
                                        high=kargs.get('TSCL.LIMIT_EL_HIGH'))

            self.time_rot.update_rotlimit(flag=kargs.get('TSCL.LIMIT_FLAG'),
                                          rot=kargs.get('TSCL.LIMIT_ROT'),
                                          link=kargs.get('TSCV.PROBE_LINK'),
                                          focus=kargs.get('TSCV.FOCUSINFO'),
                                          focus2=kargs.get('TSCV.FOCUSINFO2'))
        except Exception as e:
            self.logger.error(f'error: target update. {e}')
