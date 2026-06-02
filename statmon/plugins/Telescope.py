#
# T. Inagaki
#
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
        self.set_spacing(0)
        self.set_margins(0, 0, 0, 0)
        self.set_layout(self.widget)

    def set_layout(self):

        self.widget.remove_all(delete=True)

        # dome part of telescope
        toplayout = Widgets.VBox()
        toplayout.set_spacing(0)
        toplayout.add_widget(self.dome_shutter)
        toplayout.add_widget(self.topscreen)

        # middle part of telescope
        middlelayout = Widgets.VBox()

        # focusing part of telescope
        telfocuslayout = Widgets.VBox()
        telfocuslayout.set_margins(0, 0, 0, 0)
        telfocuslayout.set_spacing(0)
        telfocuslayout.add_widget(self.z)
        telfocuslayout.add_widget(self.m2)
        telfocuslayout.add_widget(self.focus)

        # telescope body
        telbodylayout = Widgets.VBox()
        telbodylayout.set_margins(0, 0, 0, 0)
        telbodylayout.set_spacing(0)
        telbodylayout.add_widget(self.m1, stretch=0)
        telbodylayout.add_widget(self.cell, stretch=0)

        middlelayout.add_widget(telfocus, stretch=0)
        middlelayout.add_widget(self.azel, stretch=5)
        middlelayout.add_widget(telbody, stretch=0)
        # middlelayout.setStretch(1, 1000)
        # middlelayout.setStretch(2, 0)

        # right layout will be combination of following components:
        # ins/img-rot, adc, tiptilt, waveplate, m3
        rightlayout = Widgets.VBox()
        self.set_focus_layout(rlayout=rightlayout)

        # combine right, middle, left layout
        telhlayout = Widgets.HBox()
        telhlayout.set_spacing(0)
        telhlayout.add_widget(self.windscreen, stretch=0)
        telhlayout.add_widget(middlelayout, stretch=5)
        telhlayout.add_widget(rightlayout, stretch=0)

        self.widget.add_widget(toplayout)
        self.widget.add_widget(telhlayout, stretch=5)

        # middlelayout.setStretch(1, 1000)
        # middlelayout.setStretch(2, 0)


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
