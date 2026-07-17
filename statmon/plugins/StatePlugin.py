#
# T. Inagaki
#
import PlBase

from CustomLabel import Label
from error import ERROR


class State(Label):
    ''' state of the telescope in pointing/slewing/tracking/guiding  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=23, fg='white', bg='darkgreen',
                         logger=logger)

    def update_state(self, state, intensity, valerr, calc_mode=None):
        self.logger.debug(f'state={state}, intensity={intensity}, valerr={valerr}, calc_mode={calc_mode}')

        sv_guiding = ("Guiding(SV1)", "Guiding(SV2)")

        bg = self.normal
        if state in ERROR:
            self.logger.debug(f'state={state} in error')
            state = "Unknown"
            bg = self.alarm

        elif state == "Slewing":
            bg = self.warn

        elif state.startswith("Guiding"):
            if intensity in ERROR or valerr in ERROR:
                bg = self.alarm
            elif intensity < 1.0:
                bg = self.alarm
            elif valerr >= 1000.0:
                bg = self.alarm
            elif valerr >= 500.0:
                bg = self.warn

            # if sv guiding, add calculation mode to state
            if state in sv_guiding:
                state = '%s(%s)' % (state, calc_mode)
                self.logger.debug(f'sv state={state}')
        # else is pointing, tracking with green color

        self.logger.debug(f'state={state}, intensity={intensity} valerr={valerr} bg={bg}')
        self.set_text(state)
        self.set_color(fg=self.fg, bg=bg)


class StatePlugin(PlBase.Plugin):

    aliases = ['STATL.TELDRIVE', 'TSCL.AG1Intensity', 'STATL.AGRERR',
               'TSCL.AG1Intensity', 'STATL.AGRERR', 'TSCL.SV1Intensity',
               'STATL.SVRERR', 'STATL.SV_CALC_MODE',
               'TSCL.HSC.SCAG.Intensity', 'TSCL.HSC.SHAG.Intensity',
               'TSCL.PFS.AG.Intensity', 'TSCL.AGFMOSIntensity']

    other_inst = set(['SPCAM', 'IRCS', 'HICIAO', 'CHARIS', 'K3D', 'MOIRCS',
                      'FOCAS', 'COMICS', 'SWIMS', 'MIMIZUKU', 'SUKA', 'IRD',
                      'VAMPIRES', 'SCEXAO', 'REACH', 'NINJA'])
    ns_opt = set(['HDS'])
    p_opt2_hsc = set(['HSC'])
    p_opt2_pfs = set(['PFS'])
    p_ir = set(['FMOS'])

    def change_config(self, controller, d):

        self.logger.info('changing config dict=%s ins=%s' %(d, d['inst']))

        obcp = d['inst']
        if obcp.startswith('#'):
            self.logger.debug('obcp is not assigned. %s' %obcp)
            return

        self.set_layout(obcp=obcp)

    def set_layout(self, obcp):
        self.obcp = obcp
        self.root.remove_all(delete=True)
        self.root.add_widget(self.state, stretch=1)

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        self.state = State(logger=self.logger)
        self.obcp = 'SUKA'

    def start(self):
        self.controller.register_select('state', self.update,
                                        self.aliases)
        self.controller.add_callback('change-config', self.change_config)

    def update(self, statusDict):

        state = statusDict.get('STATL.TELDRIVE')
        calc_mode = None
        # if not guiding, intensity and valerr don't matter
        intensity = None
        valerr = None

        if self.obcp in self.p_opt2_hsc:
            if state == "Guiding(HSCSCAG)":
                intensity = statusDict.get('TSCL.HSC.SCAG.Intensity')
                valerr = statusDict.get('STATL.AGRERR')
            elif state == "Guiding(HSCSHAG)":
                intensity = statusDict.get('TSCL.HSC.SHAG.Intensity')
                valerr = statusDict.get('STATL.AGRERR')

        elif self.obcp in self.p_opt2_pfs:
            if state == "Guiding(PFSAG)":
                intensity = statusDict.get('TSCL.PFS.AG.Intensity')
                valerr = statusDict.get('STATL.AGRERR')

        elif self.obcp in self.other_inst:
            if state == "Guiding(AG1)":
                intensity = statusDict.get('TSCL.AG1Intensity')
                valerr = statusDict.get('STATL.AGRERR')
            elif state == "Guiding(AG2)":
                intensity = statusDict.get('TSCL.AG2Intensity')
                valerr = statusDict.get('STATL.AGRERR')

        elif self.obcp in self.ns_opt:
            if state == "Guiding(SV1)":
                intensity = statusDict.get('TSCL.SV1Intensity')
                valerr = statusDict.get('STATL.SVRERR')
                calc_mode = statusDict.get('STATL.SV_CALC_MODE')
            elif state == "Guiding(SV2)":
                intensity = statusDict.get('TSCL.SV2Intensity')
                valerr = statusDict.get('STATL.SVRERR')
                calc_mode = statusDict.get('STATL.SV_CALC_MODE')
            elif state == "Guiding(AG1)":
                intensity = statusDict.get('TSCL.AG1Intensity')
                valerr = statusDict.get('STATL.AGRERR')
            elif state == "Guiding(AG2)":
                intensity = statusDict.get('TSCL.AG2Intensity')
                valerr = statusDict.get('STATL.AGRERR')

        elif self.obcp in self.p_ir:
            if state in ["Guiding(AGPIR)", "Guiding(AGFMOS)"]:
                intensity = statusDict.get('TSCL.AGFMOSIntensity')
                valerr = statusDict.get('STATL.AGRERR')

        self.state.update_state(state=state, intensity=intensity,
                                valerr=valerr, calc_mode=calc_mode)
