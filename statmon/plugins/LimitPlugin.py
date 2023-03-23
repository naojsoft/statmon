from ginga.gw import Widgets

import PlBase
import Limit


class AzLimitPlugin(PlBase.Plugin):
    """ Az Limit """
    aliases = ['TSCS.AZ', 'TSCS.AZ_CMD']

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        title = 'AZ'
        alarm = [-269.5, 269.5]
        warn = [-260.0, 260.0 ]
        limit = [-270.0, 270.0]
        self.limit = Limit.Limit(title=title, alarm=alarm, warn=warn,
                                 limit=limit, logger=self.logger)
        self.root.add_widget(Widgets.wrap(self.limit), stretch=1)

    def start(self):
        self.controller.register_select('azlimit', self.update, AzLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur = statusDict.get(AzLimitPlugin.aliases[0])
        cmd = statusDict.get(AzLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class ElLimitPlugin(PlBase.Plugin):
    """ El Limit """
    aliases=['TSCS.EL', 'TSCS.EL_CMD', 'STATL.TELDRIVE']

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        title = 'EL'
        marker = 15.0
        marker_txt = 15.0
        warn = [15.0, 89.0]
        alarm = [10.0,89.5]
        limit = [10.0, 90.0]

        self.limit = Limit.Limit(title=title, alarm=alarm, warn=warn, limit=limit, marker=marker, marker_txt=marker_txt, logger=self.logger)
        self.root.add_widget(Widgets.wrap(self.limit), stretch=1)

    def start(self):
        self.controller.register_select('ellimit', self.update, ElLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur = statusDict.get(ElLimitPlugin.aliases[0])
        cmd = statusDict.get(ElLimitPlugin.aliases[1])
        state=statusDict.get(ElLimitPlugin.aliases[2])
        self.limit.update_limit(current=cur, cmd=cmd, state=state)


class RotLimitPlugin(PlBase.Plugin):
    """ Rotator Limit """

    def __set_aliases(self, obcp):

        if obcp in PlBase.pf_inst:
            self.aliases = ['TSCS.INSROTPOS_PF', 'TSCS.INSROTCMD_PF']
        elif obcp in PlBase.cs_inst:
            self.aliases = ['TSCS.INSROTPOS', 'TSCS.INSROTCMD']
        elif obcp in PlBase.ns_inst:
            self.aliases = ['TSCS.ImgRotPos', 'TSCS.IMGROTCMD']
        else:
            self.aliases = [None, None]

    def __set_limit(self, obcp):

        # instrument name: title, warn, alarm,  limit
        limit = {'SPCAM': ('Rotator Popt', (-240.0, 240.0), (-249.5, 249.5), (-250.0, 250.0)),
                 'HSC': ('Rotator Popt2',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'PFS': ('Rotator Popt2',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'FMOS': ('Rotator Pir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'HDS': ('Rotator Ns Opt', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'IRCS': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'HICIAO': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'CHARIS': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'IRD': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'K3D': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'COMICS': ('Rotator Cs',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'SWIMS': ('Rotator Cs',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'MIMIZUKU': ('Rotator Cs',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'MOIRCS': ('Rotator Cs',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'FOCAS': ('Rotator Cs',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'SUKA': ('Rotator Cs',  (-260.0, 260.0), (-269.5, 269.5), (-270.0, 270.0)),
                 'VAMPIRES': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
                 'SCEXAO': ('Rotator Ns Ir', (-175.0, 175.0), (-179.5, 179.5), (-180.0, 180.0)),
        }

        try:
            self.title, self.warn, self.alarm, self.limit = limit[obcp]
        except Exception as e:
            self.logger.error('error: seting limit. %s' %e)
            self.title, self.warn, self.alarm, self.limit = None

    def set_layout(self, obcp):

        self.__set_aliases(obcp)
        self.__set_limit(obcp)

        self.logger.debug('rotator-limit setlayout. obcp=%s aliases=%s  title=%s' %(obcp, self.aliases, self.title))

        self.limit_rot = Limit.Limit(title=self.title, alarm=self.alarm,
                                     warn=self.warn, limit=self.limit,
                                     logger=self.logger)

        self.root.remove_all(delete=True)
        self.root.add_widget(Widgets.wrap(self.limit_rot), stretch=1)

    def change_config(self, controller, d):

        self.logger.debug('rotator-limit changing config dict=%s ins=%s' %(d, d['inst']))

        obcp = d['inst']
        if obcp.startswith('#'):
            self.logger.debug('obcp is not assigned. %s' %obcp)
            return

        self.set_layout(obcp=obcp)
        controller.register_select('rotlimit', self.update, self.aliases)

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
        self.controller.register_select('rotlimit', self.update, self.aliases)
        self.controller.add_callback('change-config', self.change_config)


    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))

        cur = statusDict.get(self.aliases[0])
        cmd = statusDict.get(self.aliases[1])
        self.limit_rot.update_limit(current=cur, cmd=cmd)


class ProbeLimitPlugin(PlBase.Plugin):
    """ Probe Limit  """

    def set_layout(self, obcp):

        self.set_aliases(obcp)
        self.set_limit(obcp)

        self.logger.debug('probe-limit obcp=%s aliases=%s title=%s' %(obcp, self.aliases, self.title))

        width = 350
        self.limit_probe = Limit.Limit(title=self.title,
                                       alarm=self.alarm, warn=self.warn,
                                       limit=self.limit, width=width,
                                       logger=self.logger)
        self.root.remove_all(delete=True)
        self.root.add_widget(Widgets.wrap(self.limit_probe), stretch=1)

    def change_config(self, controller, d):

        self.logger.debug('probe-limit changing config dict=%s ins=%s' %(d, d['inst']))

        obcp = d['inst']
        if obcp.startswith('#'):
            self.logger.debug('obcp is not assigned. %s' %obcp)
            return

        try:
            if not (self.obcp in self.ao or self.obcp in self.popt2):
                self.root.remove_all(delete=True)
        except Exception as e:
            self.logger.error('error: deleting current layout. %s' %e)
        else:
            if not (obcp in self.ao or obcp in self.popt2):
                self.set_layout(obcp=obcp)
                controller.register_select(self.register_name, self.update,
                                           self.aliases)
        finally:
            self.obcp = obcp


    def build_gui(self, container):

        self.popt = 'SPCAM'
        self.pir = 'FMOS'
        # telescope (non-instrument) guiders
        self.ag = ('MOIRCS', 'FOCAS', 'COMICS', 'HDS', 'SWIMS', 'MIMIZUKU',
                   'SUKA')
        self.ao = PlBase.ao_inst
        self.popt2 = ('HSC', 'PFS')

        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        try:
            self.obcp = self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
            self.set_layout(obcp=self.obcp)
        except Exception as e:
            self.logger.error('error: building layout. %s' %e)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))

        cur = statusDict.get(self.aliases[0])
        cmd = statusDict.get(self.aliases[1])
        self.limit_probe.update_limit(current=cur, cmd=cmd)


class Probe1LimitPlugin(ProbeLimitPlugin):
    """ AG Probe R/X Limit  """

    def set_aliases(self, obcp):

        #self.logger.info('Probe1LimitPlugin obcp <%s>' %obcp)

        if obcp in self.ag:
            self.aliases = ['TSCV.AGR', 'TSCL.AG_R_CMD']
            #self.aliases = ['TSCL.AG_R', 'TSCL.AG_R_CMD']
        elif obcp == self.popt:
            self.aliases = ['TSCL.AGPF_X', 'TSCL.AGPF_X_CMD']
        elif obcp == self.pir:
            self.aliases = ['TSCL.AGPIR_X', 'TSCL.AGPIR_X_CMD']
        else:
            self.aliases = [None, None]

    def set_limit(self, obcp):

        # instrument name: title, warn, alarm,  limit
        limit = {'SPCAM': ('Ag-X Popt', (0.0, 170.0), (0.0, 170.0), (0.0, 170.0)),
                 'FMOS': ('Ag-X Pir', (-9.0, 239.0), (-10.0, 240.0), (-10.0, 240.0)),
                 'HDS': ('Ag_R Ns Opt', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0)),
                 'COMICS': ('Ag-R Cs', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0)),
                 'MOIRCS': ('Ag-R Cs', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0)),
                 'FOCAS': ('Ag-R Cs', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0)),
                 'SUKA': ('Ag-R Cs', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0)),
                 'SWIMS': ('Ag-R Cs', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0)),
                 'MIMIZUKU': ('Ag-R Cs', (0.0, 140.0), (0.0, 140.0), (-5.0, 145.0))
                 }

        try:
            self.title, self.warn, self.alarm, self.limit = limit[obcp]
        except Exception as e:
            self.logger.error('error: seting limit. %s' %e)
            self.title, self.warn, self.alarm, self.limit = None

    def start(self):
        self.register_name = 'probe1limit'
        self.controller.register_select(self.register_name, self.update, self.aliases)
        self.controller.add_callback('change-config', self.change_config)


class Probe2LimitPlugin(ProbeLimitPlugin):
    """ AG Probe Theta/Y Limit  """

    def set_aliases(self, obcp):

        if obcp in self.ag:
            self.aliases = ['TSCV.AGTheta', 'TSCL.AG_THETA_CMD']
        elif obcp == self.popt:
            self.aliases = ['TSCL.AGPF_Y', 'TSCL.AGPF_Y_CMD']
        elif obcp == self.pir:
            self.aliases = ['TSCL.AGPIR_Y', 'TSCL.AGPIR_Y_CMD']
        else:
            self.aliases = [None, None]

    def set_limit(self, obcp):

        # instrument name: title, warn, alarm,  limit
        limit = {'SPCAM': ('Ag-Y Popt', (-20.0, 20.0), (-20.0, 20.0), (-20.0, 20.0)),
                 'FMOS': ('Ag-Y Pir', (-40.0, 40.0), (-40.0, 40.0), (-40.0, 40.0)),
                 'HDS': ('Ag_Theta Ns Opt', (-270.0, 270.0), (-270.0, 270.0), (-270.0, 270.0)),
                 'COMICS': ('Ag-Theta Cs', (-185.0, 185.0), (-185.0, 185.0), (-185.0, 185.0)),
                 'MOIRCS': ('Ag-Theta Cs', (-185.0, 185.0), (-185.0, 185.0), (-185.0, 185.0)),
                 'FOCAS': ('Ag-Theta Cs', (-185.0, 185.0), (-185.0, 185.0), (-185.0, 185.0)),
                 'SUKA': ('Ag-Theta Cs', (-185.0, 185.0), (-185.0, 185.0), (-185.0, 185.0)),
                 'SWIMS': ('Ag-Theta Cs', (-185.0, 185.0), (-185.0, 185.0), (-185.0, 185.0)),
                 'MIMIZUKU': ('Ag-Theta Cs', (-185.0, 185.0), (-185.0, 185.0), (-185.0, 185.0)),}

        try:
            self.title, self.warn, self.alarm, self.limit = limit[obcp]
        except Exception as e:
            self.logger.error('error: seting limit. %s' %e)
            self.title, self.warn, self.alarm, self.limit = None

    def start(self):
        self.register_name = 'probe2limit'
        self.controller.register_select(self.register_name, self.update, self.aliases)
        self.controller.add_callback('change-config', self.change_config)
