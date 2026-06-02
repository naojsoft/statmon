#
# T. Inagaki
#
import PlBase

from ginga.gw import Widgets

from DomeShutter import DomeShutter
from Topscreen import Topscreen
from Windscreen import Windscreen
from FocusZ import FocusZ
from Focus import Focus
from AzEl import AzEl
from M2 import M2
from M1Cover import M1Cover
from CellCover import CellCover
import InsRot
import ImgRot
import Adc
from TipChop import TipChop
from Waveplate import Waveplate
from AoShutter import AoShutter
from Dummy import Dummy
from M3 import M3


class TelescopeGui:
    def __init__(self, parent=None, obcp=None, logger=None):

        self.obcp = obcp
        self.logger = logger
        self.dome_shutter = DomeShutter(logger=logger)
        self.topscreen = Topscreen(logger=logger)
        self.windscreen = Windscreen(logger=logger)
        self.z = FocusZ(logger=logger)
        self.focus = Focus(logger=logger)
        self.azel = AzEl(logger=logger)
        self.m2 = M2(logger=logger)
        self.m1 = M1Cover(logger=logger)
        #self.m3 = M3(logger=logger)
        self.cell = CellCover(logger=logger)

        self.widget = Widgets.VBox()
        self.widget.set_spacing(0)
        self.widget.set_margins(0, 0, 0, 0)
        self.set_layout()

    def get_widget(self):
        return self.widget

    def set_layout(self):

        self.widget.remove_all(delete=True)

        # dome part of telescope
        top = Widgets.VBox()
        top.set_spacing(0)
        top.add_widget(self.dome_shutter)
        top.add_widget(self.topscreen)

        # middle part of telescope
        middle = Widgets.VBox()

        # focusing part of telescope
        telfocus = Widgets.VBox()
        telfocus.set_margins(0, 0, 0, 0)
        telfocus.set_spacing(0)
        telfocus.add_widget(self.z)
        telfocus.add_widget(self.m2)
        telfocus.add_widget(self.focus)

        # telescope body
        telbody = Widgets.VBox()
        telbody.set_margins(0, 0, 0, 0)
        telbody.set_spacing(0)
        telbody.add_widget(self.m1, stretch=0)
        telbody.add_widget(self.cell, stretch=0)

        middle.add_widget(telfocus, stretch=0)
        middle.add_widget(self.azel, stretch=5)
        middle.add_widget(telbody, stretch=0)
        # middle.setStretch(1, 1000)
        # middle.setStretch(2, 0)

        # right layout will be combination of following components:
        # ins/img-rot, adc, tiptilt, waveplate, m3
        right = Widgets.VBox()
        self.set_focus_layout(rlayout=right)

        # combine right, middle, left layout
        telh = Widgets.HBox()
        telh.set_spacing(0)
        telh.add_widget(self.windscreen, stretch=0)
        telh.add_widget(middle, stretch=5)
        telh.add_widget(right, stretch=0)

        self.widget.add_widget(top)
        self.widget.add_widget(telh, stretch=5)

        # middle.setStretch(1, 1000)
        # middle.setStretch(2, 0)


    def popt_layout(self, rlayout):
        ''' prime focus optical'''
        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=95, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)

        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.insrot = InsRot.InsRotPf(logger=self.logger)
        r2layout.add_widget(self.insrot)

        self.adc = Adc.AdcPf(logger=self.logger)
        r2layout.add_widget(self.adc)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=285, logger=self.logger)
        r2layout.add_widget(empty_shell)

        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def pir_layout(self, rlayout):
        ''' prime focus infrared'''
        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=95, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)

        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.insrot = InsRot.InsRotPf(logger=self.logger)
        r2layout.add_widget(self.insrot)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=320, logger=self.logger)
        r2layout.add_widget(empty_shell)

        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def nsopt_layout(self, rlayout):
        ''' nasmyth focus optical'''
        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=95, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)

        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.imgrot = ImgRot.ImgRotNsOpt(logger=self.logger)
        r2layout.add_widget(self.imgrot)

        self.adc = Adc.Adc(logger=self.logger)
        r2layout.add_widget(self.adc)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=277, logger=self.logger)
        r2layout.add_widget(empty_shell)

        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def nsir_layout(self, rlayout):
        ''' nasmyth focus infrared'''

        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=95, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)
        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)
        self.imgrot = ImgRot.ImgRotNsIr(logger=self.logger)
        r2layout.add_widget(self.imgrot)
        self.waveplate = Waveplate(logger=self.logger)
        r2layout.add_widget(self.waveplate)
        empty_shell = Dummy(height=30, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.aoshutter = AoShutter(logger=self.logger)
        r2layout.add_widget(self.aoshutter)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=150, logger=self.logger)
        r2layout.add_widget(empty_shell)
        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def cs_layout(self, rlayout):
        ''' cassegrain focus '''
        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=95, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)
        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.insrot = InsRot.InsRotCs(logger=self.logger)
        r2layout.add_widget(self.insrot)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=320, logger=self.logger)
        r2layout.add_widget(empty_shell)

        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def csir_layout(self, rlayout):
        ''' cassegrain focus infrared '''

        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=25, logger=self.logger)
        r1layout.add_widget(empty_shell)

        self.tipchop = TipChop(logger=self.logger)
        r1layout.add_widget(self.tipchop)

        empty_shell = Dummy(height=35, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)

        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.insrot = InsRot.InsRotCs(logger=self.logger)
        r2layout.add_widget(self.insrot)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=320, logger=self.logger)
        r2layout.add_widget(empty_shell)

        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def csopt_layout(self, rlayout):
        ''' cassegrain focus optical '''

        r1layout = Widgets.VBox()
        empty_shell = Dummy(height=95, logger=self.logger)
        r1layout.add_widget(empty_shell)

        r2layout = Widgets.VBox()
        r2layout.set_spacing(1)
        empty_shell = Dummy(height=1, logger=self.logger)
        r2layout.add_widget(empty_shell)

        self.insrot = InsRot.InsRotCs(logger=self.logger)
        r2layout.add_widget(self.insrot)

        self.adc = Adc.Adc(logger=self.logger)
        r2layout.add_widget(self.adc)

        self.m3 = M3(logger=self.logger)
        r2layout.add_widget(self.m3)

        empty_shell = Dummy(height=285, logger=self.logger)
        r2layout.add_widget(empty_shell)

        rlayout.add_widget(r1layout)
        rlayout.add_widget(r2layout)

    def set_focus_layout(self, rlayout):
        ''' spcam/hsc: insrot,adc
            fmos: insrot
            hds:  imgrot,adc
            ircs/hiciao/k3d/charis/vampires/scexao: imgrot,waveplate
            comics: insrot,tipchop
            focas: insrot,adc
            moircs insrot
        '''
        focus = {'HDS': self.nsopt_layout, 'SPCAM': self.popt_layout,
                 'HICIAO': self.nsir_layout, 'IRCS': self.nsir_layout,
                 'CHARIS': self.nsir_layout, 'IRD': self.nsir_layout,
                 'FMOS': self.pir_layout, 'HSC': self.popt_layout,
                 'K3D': self.nsir_layout, 'MOIRCS': self.cs_layout,
                 'SWIMS': self.csir_layout, 'MIMIZUKU' : self.csir_layout,
                 'FOCAS': self.csopt_layout, 'COMICS': self.csir_layout,
                 'SUKA': self.cs_layout, 'PFS': self.popt_layout,
                 'VAMPIRES': self.nsir_layout, 'SCEXAO': self.nsir_layout,
                 'REACH': self.nsir_layout, 'NINJA': self.nsir_layout}

        self.logger.debug(f'telescope focuslayout ins={self.obcp}')

        try:
            focus[self.obcp](rlayout)
        except Exception as e:
            self.logger.error(f'error: setting focus layout. {e}')
            pass


class Telescope(TelescopeGui):

    def __init__(self, parent=None, obcp=None, logger=None):
        super(Telescope, self).__init__(parent=parent, obcp=obcp, logger=logger)

    def update_nsir(self, **kargs):
        self.imgrot.update_imgrot(imgrot=kargs.get('TSCV.ImgRotRotation'),
                                  mode=kargs.get('TSCV.ImgRotMode'),
                                  focus=kargs.get('TSCV.FOCUSINFO'),
                                  itype=kargs.get('TSCV.ImgRotType'))

        self.waveplate.update_waveplate(stage1=kargs.get('WAV.STG1_PS'),
                                        stage2=kargs.get('WAV.STG2_PS'),
                                        stage3=kargs.get('WAV.STG3_PS'))

        self.aoshutter.update_aoshutter(lwsh=kargs.get('AON.LWFS.LASH'),
                                        hwsh=kargs.get('AON.HWFS.LASH'))


    def update_csir(self, **kargs):
        self.tipchop.update_tipchop(mode=kargs.get('TSCV.TT_Mode'),
                                    drive=kargs.get('TSCV.TT_Drive'),
                                    data=kargs.get('TSCV.TT_DataAvail'),
                                    state=kargs.get('TSCV.TT_ChopStat'))

        self.insrot.update_insrot(insrot=kargs.get('TSCV.InsRotRotation'),
                                  mode=kargs.get('TSCV.InsRotMode'))

    def update_csopt(self, **kargs):

        self.insrot.update_insrot(insrot=kargs.get('TSCV.InsRotRotation'),
                                  mode=kargs.get('TSCV.InsRotMode'))

        self.adc.update_adc(on_off=kargs.get('TSCV.ADCOnOff'),
                            mode=kargs.get('TSCV.ADCMode'),
                            in_out=kargs.get('TSCV.ADCInOut'))

    def update_cs(self, **kargs):
        self.insrot.update_insrot(insrot=kargs.get('TSCV.InsRotRotation'),
                                  mode=kargs.get('TSCV.InsRotMode'))

    def update_pir(self, **kargs):

        self.insrot.update_insrot(insrot=kargs.get('TSCV.INSROTROTATION_PF'),
                                  mode=kargs.get('TSCV.INSROTMODE_PF'))

    def update_popt(self, **kargs):

        self.insrot.update_insrot(insrot=kargs.get('TSCV.INSROTROTATION_PF'),
                                  mode=kargs.get('TSCV.INSROTMODE_PF'))

        self.adc.update_adc(on_off=kargs.get('TSCV.ADCONOFF_PF'),
                            mode=kargs.get('TSCV.ADCMODE_PF'))

    def update_nsopt(self, **kargs):

        self.imgrot.update_imgrot(imgrot=kargs.get('TSCV.ImgRotRotation'),
                                  mode=kargs.get('TSCV.ImgRotMode'),
                                  focus=kargs.get('TSCV.FOCUSINFO'),
                                  itype=kargs.get('TSCV.ImgRotType'))

        self.adc.update_adc(on_off=kargs.get('TSCV.ADCOnOff'),
                            mode=kargs.get('TSCV.ADCMode'),
                            in_out=kargs.get('TSCV.ADCInOut'))

    def update_focus(self, **kargs):

        focus = {'HDS': self.update_nsopt, 'SPCAM': self.update_popt,
                 'HICIAO': self.update_nsir, 'IRCS': self.update_nsir,
                 'CHARIS': self.update_nsir, 'IRD': self.update_nsir,
                 'FMOS': self.update_pir, 'HSC': self.update_popt,
                 'K3D': self.update_nsir, 'MOIRCS': self.update_cs,
                 'SWIMS':  self.update_cs, 'MIMIZUKU' :  self.update_cs,
                 'FOCAS': self.update_csopt, 'COMICS': self.update_csir,
                 'SUKA': self.update_cs, 'PFS': self.update_popt,
                 'VAMPIRES': self.update_nsir, 'SCEXAO': self.update_nsir,
                 'REACH': self.update_nsir, 'NINJA': self.update_nsir}

        self.m3.update_m3(m3=kargs.get('TSCV.M3Drive'))

        try:
            focus[self.obcp](**kargs)
        except Exception as e:
            self.logger.error(f'error: updating focus. obcp={self.obcp}.  {e}')

    def update_telescope(self, **kargs):

        self.logger.debug(f'updating telescope. kargs={kargs}')

        self.dome_shutter.update_dome(dome=kargs.get('STATL.DOMESHUTTER_POS'))
        #self.dome_shutter.update_dome(dome=kargs.get('TSCV.DomeShutter'))
        self.topscreen.update_topscreen(mode=kargs.get('TSCV.TopScreen'),
                                        front=kargs.get('TSCL.TSFPOS'),
                                        rear=kargs.get('TSCL.TSRPOS'))

        self.windscreen.update_windscreen(drv=kargs.get('TSCV.WINDSDRV'),
                                          windscreen=kargs.get('TSCV.WindScreen'),
                                          cmd=kargs.get('TSCL.WINDSCMD'),
                                          pos=kargs.get('TSCL.WINDSPOS'),
                                          el=kargs.get('TSCS.EL'))

        self.z.update_z(z=kargs.get('TSCL.Z'))

        self.m2.update_m2(focus=kargs.get('STATL.M2_DESCR'))

        self.focus.update_focus(focus=kargs.get('STATL.FOC_DESCR'),
                                alarm=kargs.get('TSCV.FOCUSALARM'))

        self.azel.update_azel(az=kargs.get('TSCS.AZ'),
                              el=kargs.get('TSCS.EL'),
                              winddir=kargs.get('TSCL.WINDD'),
                              windspeed=kargs.get('TSCL.WINDS_O'),
                              state=kargs.get('STATL.TELDRIVE'))


        self.m1.update_m1cover(m1cover=kargs.get('TSCV.M1Cover'),
                               m1cover_onway=kargs.get('TSCV.M1CoverOnway'))

        self.cell.update_cell(cell=kargs.get('TSCV.CellCover'))

        self.update_focus(**kargs)


class TelescopePlugin(PlBase.Plugin):
    """ Telescope Plugin"""

    aliases = ['STATL.DOMESHUTTER_POS', 'TSCV.TopScreen', 'TSCL.TSFPOS',
               'TSCL.TSRPOS', 'TSCV.WINDSDRV', 'TSCV.WindScreen',
               'TSCL.WINDSPOS', 'TSCL.WINDSCMD', 'TSCL.WINDD', 'TSCL.Z',
               'STATL.FOC_DESCR', 'STATL.M2_DESCR', 'TSCV.FOCUSALARM',
               'TSCS.AZ', 'STATL.TELDRIVE', 'TSCS.EL',
               'TSCV.M1Cover', 'TSCV.M1CoverOnway', 'TSCV.CellCover',
               'TSCV.ADCONOFF_PF', 'TSCV.ADCMODE_PF',
               'TSCV.ADCOnOff', 'TSCV.ADCMode', 'TSCV.ADCInOut',
               'TSCV.ImgRotRotation', 'TSCV.ImgRotMode', 'TSCV.ImgRotType',
               'TSCV.FOCUSINFO',
               'TSCV.INSROTROTATION_PF', 'TSCV.INSROTMODE_PF',
               'TSCV.InsRotRotation', 'TSCV.InsRotMode',
               'WAV.STG1_PS', 'WAV.STG2_PS', 'WAV.STG3_PS',
               'TSCV.TT_Mode', 'TSCV.TT_Drive', 'TSCV.TT_DataAvail',
               'TSCV.TT_ChopStat', 'TSCL.WINDS_O',
               'AON.LWFS.LASH', 'AON.HWFS.LASH', 'TSCV.M3Drive']

    def set_layout(self, obcp):

        self.telescope = Telescope(obcp=obcp, logger=self.logger)
        self.logger.debug('telescope setlayout ins=%s' %(obcp))

        self.root.remove_all(delete=True)
        self.root.add_widget(self.telescope.get_widget(), stretch=1)

    def change_config(self, controller, d):

        self.logger.debug('telescope change config dict=%s ins=%s' %(d, d['inst']))
        obcp = d['inst']
        if obcp.startswith('#'):
            self.logger.debug('obcp is not assigned. %s' %obcp)
            return

        try:
            self.set_layout(obcp=obcp)
        except Exception as e:
            self.logger.error(f"error configuring layout: {e}")

    def build_gui(self, container):

        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        try:
            self.obcp = 'SUKA'
            self.set_layout(self.obcp)

        except Exception as e:
            self.logger.error(f"error building layout: {e}",
                              exc_info=True)

    def start(self):
        self.controller.register_select('telescope', self.update, \
                                         TelescopePlugin.aliases)
        self.controller.add_callback('change-config', self.change_config)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        self.telescope.update_telescope(**statusDict)
