from ginga.gw import Widgets

from qtpy import QtWidgets, QtCore
import sip

import PlBase
import State


class StatePlugin(PlBase.Plugin):

    def __set_aliases(self, obcp):

        other = ('SPCAM', 'IRCS', 'HICIAO', 'CHARIS', 'K3D', 'MOIRCS', 'FOCAS', 'COMICS', 'SWIMS', 'MIMIZUKU', 'SUKA', 'IRD', 'VAMPIRES', 'SCEXAO')
        ns_opt = ('HDS',)
        p_opt2_hsc = ('HSC',)
        p_opt2_pfs = ('PFS',)
        p_ir = ('FMOS',)


        if obcp in other:
            self.aliases = ['STATL.TELDRIVE', \
                            'TSCL.AG1Intensity', 'STATL.AGRERR']
        elif obcp in ns_opt:
            self.aliases = ['STATL.TELDRIVE', \
                            'TSCL.AG1Intensity', 'STATL.AGRERR', \
                            'TSCL.SV1Intensity', 'STATL.SVRERR', \
                            'STATL.SV_CALC_MODE']
        elif obcp in p_opt2_hsc:
            self.aliases = ['STATL.TELDRIVE', \
                            'TSCL.HSC.SCAG.Intensity', 'STATL.AGRERR', \
                            'TSCL.HSC.SHAG.Intensity', 'STATL.AGRERR']
        elif obcp in p_opt2_pfs:
            self.aliases = ['STATL.TELDRIVE', \
                            'TSCL.PFS.AG.Intensity', 'STATL.AGRERR']
        elif obcp in p_ir:
            self.aliases = ['STATL.TELDRIVE', \
                            'TSCL.AGFMOSIntensity', 'STATL.AGRERR']


    def change_config(self, controller, d):

        self.logger.info('changing config dict=%s ins=%s' %(d, d['inst']))

        obcp = d['inst']
        if obcp.startswith('#'):
            self.logger.debug('obcp is not assigned. %s' %obcp)
            return

        self.set_layout(obcp=obcp)
        controller.register_select('state', self.update, self.aliases)

    def set_layout(self, obcp):

        self.__set_aliases(obcp)

        self.state = State.State(parent=self.root.get_widget(),
                                 logger=self.logger)

        self.root.remove_all(delete=True)
        self.root.add_widget(Widgets.wrap(self.state), stretch=1)

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        try:
            obcp = self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
            self.set_layout(obcp)
        except Exception as e:
            self.logger.error('error: building layout. %s' %e)

    def start(self):
        self.controller.register_select('state', self.update, self.aliases)
        self.controller.add_callback('change-config', self.change_config)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))

        state = statusDict.get(self.aliases[0])

        guiding1 = ["Guiding(AG1)", "Guiding(AG2)", "Guiding(AGFMOS)", \
                    "Guiding(AGPIR)", "Guiding(HSCSCAG)", "Guiding(PFSAG)"]
        sv = ["Guiding(SV1)", "Guiding(SV2)"]
        guiding2 = sv + ["Guiding(HSCSHAG)"]


        if state in guiding1:
            intensity = statusDict.get(self.aliases[1])
            valerr = statusDict.get(self.aliases[2])
        elif state in guiding2:
            intensity = statusDict.get(self.aliases[3])
            valerr = statusDict.get(self.aliases[4])
        else:  # if not guiding, intensity and valerr don't matter.
            intensity = valerr = None

        if state in sv:
            calc_mode = statusDict.get(self.aliases[5])
        else:
            calc_mode = None

        self.state.update_state(state=self.state, intensity=intensity,
                                valerr=valerr, calc_mode=calc_mode)
