import PlBase
import Limit
from PyQt4 import QtGui, QtCore

class AzLimitPlugin(PlBase.Plugin):
    """ Az Limit """
    aliases=['TSCS.AZ', 'TSCS.AZ_CMD']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        title='AZ'
        alarm=[-269.5, 269.5]
        warn=[-260.0, 260.0 ]
        limit=[-270.0, 270.0]
        self.limit =  Limit.Limit(parent=qtwidget, title=title, alarm=alarm, warn=warn, limit=limit, logger=self.logger)
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('azlimit', self.update, AzLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(AzLimitPlugin.aliases[0])
        cmd=statusDict.get(AzLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class ElLimitPlugin(PlBase.Plugin):
    """ El Limit """
    aliases=['TSCS.EL', 'TSCS.EL_CMD', 'STATL.TELDRIVE']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        title='EL'
        marker=15.0
        marker_txt=15.0
        warn=[15.0, 89.0]
        alarm=[10.0,89.5] 
        limit=[10.0, 90.0]   

        self.limit =  Limit.Limit(parent=qtwidget, title=title, alarm=alarm, warn=warn, limit=limit, marker=marker, marker_txt=marker_txt, logger=self.logger)
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('ellimit', self.update, ElLimitPlugin.aliases)
    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(ElLimitPlugin.aliases[0])
        cmd=statusDict.get(ElLimitPlugin.aliases[1])
        state=statusDict.get(ElLimitPlugin.aliases[2])
        self.limit.update_limit(current=cur, cmd=cmd, state=state)

class PfInsRotLimitPlugin(PlBase.Plugin):
    """ Prime Rotator Limit """
    aliases=['TSCS.INSROTPOS_PF', 'TSCS.INSROTCMD_PF']

    def build_gui(self, container, title, alarm, warn, limit):
        self.root = container
        qtwidget = QtGui.QWidget()
        title=title
        alarm=alarm
        warn=warn
        limit=limit

        self.limit = Limit.Limit(parent=qtwidget, title=title, alarm=alarm, \
                                 warn=warn, limit=limit, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(PfInsRotLimitPlugin.aliases[0])
        cmd=statusDict.get(PfInsRotLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class PoptInsRotLimitPlugin(PfInsRotLimitPlugin):
    """ Popt Rotator Limit  """
  
    def build_gui(self, container):
        title='Rotator Popt'
        alarm=[-249.5, 249.5]
        warn=[-240.0, 240.0 ]
        limit=[-250.0, 250.0]
        super(PoptInsRotLimitPlugin, self).build_gui(container, title, \
                                                     alarm, warn, limit) 
        #PfInsRotLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
        self.controller.register_select('poptlimit', self.update, PfInsRotLimitPlugin.aliases)


class Popt2InsRotLimitPlugin(PfInsRotLimitPlugin):
    """ Popt2 Rotator Limit """
  
    def build_gui(self, container):
        title='Rotator Popt2'
        warn=[-260.0, 260.0]
        alarm=[-269.5, 269.5]
        limit=[-270.0, 270.0]
        super(Popt2InsRotLimitPlugin, self).build_gui(container, title, \
                                                      alarm, warn, limit) 
 
    def start(self):
        self.controller.register_select('popt2limit', self.update, PfInsRotLimitPlugin.aliases)


class PirInsRotLimitPlugin(PfInsRotLimitPlugin):
    """ Pir Rotator Limit """
  
    def build_gui(self, container):

        title='Rotator Pir'
        warn=[-175.0,175.0]
        alarm=[-179.5,179.5]
        limit=[-180.0, 180.0]
        PfInsRotLimitPlugin.build_gui(self, container, title, alarm, warn, limit) 

    def start(self):
        self.controller.register_select('pirlimit', self.update, PfInsRotLimitPlugin.aliases)

class NsImgRotLimitPlugin(PlBase.Plugin):
    """ Ns Image Rotator Limit """
    aliases=['TSCS.ImgRotPos', 'TSCS.IMGROTCMD']
  
    def build_gui(self, container, title):
        self.root = container

        qtwidget = QtGui.QWidget()
        title=title
        warn=[-175.0,175.0]
        alarm=[-179.5,179.5]
        limit=[-180.0, 180.0]
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit,logger=self.logger)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(NsImgRotLimitPlugin.aliases[0])
        cmd=statusDict.get(NsImgRotLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)

class NsIrImgRotLimitPlugin(NsImgRotLimitPlugin):
    """ NsIr Image Rotator Limit """
    def build_gui(self, container):
         title='Rotator Ns Ir'
         super(NsIrImgRotLimitPlugin, self).build_gui(container, title) 

    def start(self):
        self.controller.register_select('nsirlimit', self.update, NsImgRotLimitPlugin.aliases)

class NsOptImgRotLimitPlugin(NsImgRotLimitPlugin):
    """ NsOpt Image Rotator Limit """
    def build_gui(self, container):
         title='Rotator Ns Opt'
         super(NsOptImgRotLimitPlugin, self).build_gui(container, title)

    def start(self):
        self.controller.register_select('nsoptlimit', self.update,NsImgRotLimitPlugin.aliases)


class CsInsRotLimitPlugin(PlBase.Plugin):
    """ Cs Instrument Rotator Limit """
    aliases=['TSCS.INSROTPOS', 'TSCS.INSROTCMD']
  
    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        title='Rotator Cs'
        warn=[-260.0, 260.0]
        alarm=[-269.5, 269.5]
        limit=[-270.0, 270.0]
        self.limit = Limit.Limit(parent=qtwidget, title=title, alarm=alarm, warn=warn, limit=limit,logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.controller.register_select('cslimit', self.update, CsInsRotLimit.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        
        cur=statusDict.get(CsInsRotLimit.aliases[0])
        cmd=statusDict.get(CsInsRotLimit.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)

class AgProbeThetaLimitPlugin(PlBase.Plugin):
    """  Ag Probe(Theta) Limit """
    aliases=['TSCV.AGTheta', 'TSCL.AG_THETA_CMD']

    def build_gui(self, container, title, alarm, warn, limit):
        self.root = container
        qtwidget = QtGui.QWidget()
        title=title
        alarm=alarm
        warn=warn
        limit=limit
        width=350
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit, width=width, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(AgProbeThetaLimitPlugin.aliases[0])
        cmd=statusDict.get(AgProbeThetaLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class AgProbeRLimitPlugin(PlBase.Plugin):
    """  Ag Probe(R) Limit """
    aliases=['TSCV.AGR', 'TSCL.AG_R_CMD']

    def build_gui(self, container, title, alarm, warn, limit):
        self.root = container
        qtwidget = QtGui.QWidget()
        title=title
        alarm=alarm
        warn=warn
        limit=limit
        width=350
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit, width=width, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(AgProbeRLimitPlugin.aliases[0])
        cmd=statusDict.get(AgProbeRLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class NsOptAgProbeThetaLimitPlugin(AgProbeThetaLimitPlugin):
    """ NsOpt Ag Probe Theta Limit  """

    def build_gui(self, container):
        title='Ag-Theta Ns Opt'
        warn=[-270.0, 270.0]
        alarm=[-270.0, 270.0]
        limit=[-270.0, 270.0]
        super(NsOptAgProbeThetaLimitPlugin, self).build_gui(container, title, \
                                                       alarm, warn, limit)
        #AgProbeThetaLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('nsoptagtheta', self.update, AgProbeThetaLimitPlugin.aliases)


class NsOptAgProbeRLimitPlugin(AgProbeRLimitPlugin):
    """ NsOpt Ag Probe R Limit  """

    def build_gui(self, container):
        title='Ag-R Ns Opt'
        warn=[0.0, 140.0]
        alarm=[0.0, 140.0]
        limit=[-5.0, 145.0]
        super(NsOptAgProbeRLimitPlugin, self).build_gui(container, title, \
                                                       alarm, warn, limit)
        #AgProbeThetaLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('nsoptagr', self.update, AgProbeRLimitPlugin.aliases)


class NsIrAgProbeRLimitPlugin(AgProbeRLimitPlugin):
    """ NsOpt Ag Probe R Limit  """

    def build_gui(self, container):
        title='Ag-R Ns Ir'
        warn=[0.0, 140.0]
        alarm=[0.0, 140.0]
        limit=[-5.0, 145.0]
        super(NsIrAgProbeRLimitPlugin, self).build_gui(container, title, \
                                                       alarm, warn, limit)
        #AgProbeThetaLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('nsiragr', self.update, AgProbeRLimitPlugin.aliases)


class NsIrAgProbeThetaLimitPlugin(AgProbeThetaLimitPlugin):
    """ NsIr Ag Probe Theta Limit """

    def build_gui(self, container):
        title='Ag-Theta Ns Ir'
        warn=[-270.0, 270.0]
        alarm=[-270.0, 270.0]
        limit=[-270.0, 270.0]
        super(NsIrAgProbeThetaLimitPlugin, self).build_gui(container, title, \
                                                      alarm, warn, limit)
        #AgProbeThetaLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
        self.controller.register_select('nsiragtheta', self.update, AgProbeThetaLimitPlugin.aliases)


class CsAgProbeThetaLimitPlugin(AgProbeThetaLimitPlugin):
    """ Cs Ag Probe Limit """

    def build_gui(self, container):
        title='Ag-Theta Cs'
        warn=[-185.0, 185.0]
        alarm=[-185.0, 185.0]
        limit=[-185.0, 185.0]
        super(CsAgProbeThetaLimitPlugin, self).build_gui(container, title, \
                                                    alarm, warn, limit) 
        #AgProbeThetaLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
        self.controller.register_select('csagtheta', self.update, AgProbeThetaLimitPlugin.aliases)

class CsAgProbeRLimitPlugin(AgProbeRLimitPlugin):
    """ Cs Ag Probe R Limit  """

    def build_gui(self, container):
        title='Ag-R Cs'
        warn=[0.0, 140.0]
        alarm=[0.0, 140.0]
        limit=[-5.0, 145.0]
        super(CsAgProbeRLimitPlugin, self).build_gui(container, title, \
                                                     alarm, warn, limit)
        #AgProbeThetaLimitPlugin.build_gui(self, container, title, alarm, warn, limit)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('csagr', self.update, AgProbeRLimitPlugin.aliases)


class PoptAgProbeXLimitPlugin(PlBase.Plugin):
    """  Popt Ag Probe(X) Limit """
    aliases=['TSCL.AGPF_X', 'TSCL.AGPF_X_CMD']

    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        title = 'Ag-X Popt'
        alarm = [0.0, 170.0]
        warn = [0.0, 170.0]
        limit = [0.0, 170.0]
        width=350
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit, width=width, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def start(self):
        self.controller.register_select('poptagx', self.update, \
                                        PoptAgProbeXLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(PoptAgProbeXLimitPlugin.aliases[0])
        cmd=statusDict.get(PoptAgProbeXLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class PoptAgProbeYLimitPlugin(PlBase.Plugin):
    """  Popt Ag Probe(Y) Limit """
    aliases=['TSCL.AGPF_Y', 'TSCL.AGPF_Y_CMD']

    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        title = 'Ag-Y Popt'
        alarm = [-20.0, 20.0]
        warn = [-20.0, 20.0]
        limit = [-20.0, 20.0]
        width=350
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit, width=width, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def start(self):
        self.controller.register_select('poptagy', self.update, \
                                        PoptAgProbeYLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(PoptAgProbeYLimitPlugin.aliases[0])
        cmd=statusDict.get(PoptAgProbeYLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)



class PirAgProbeXLimitPlugin(PlBase.Plugin):
    """  Pir Ag Probe(X) Limit """
    aliases=['TSCL.AGPIR_X', 'TSCL.AGPIR_X_CMD']

    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        title = 'Ag-X Pir'
        alarm = [-10.0, 240.0]
        warn = [-9.0, 239.0]
        limit = [-10.0, 240.0]
        width=350
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit, width=width, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def start(self):
        self.controller.register_select('piragx', self.update, \
                                        PirAgProbeXLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(PirAgProbeXLimitPlugin.aliases[0])
        cmd=statusDict.get(PirAgProbeXLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)


class PirAgProbeYLimitPlugin(PlBase.Plugin):
    """  Popt Ag Probe(Y) Limit """
    aliases=['TSCL.AGPF_Y', 'TSCL.AGPF_Y_CMD']

    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        title = 'Ag-Y Pir'
        alarm = [-20.0, 20.0]
        warn = [-19.0, 19.0]
        limit = [-20.0, 20.0]
        width=350
        self.limit = Limit.Limit(parent=qtwidget, title=title, \
                                 alarm=alarm, warn=warn, \
                                 limit=limit, width=width, logger=self.logger)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.limit,stretch=1)
        container.setLayout(layout)

    def start(self):
        self.controller.register_select('piragy', self.update, \
                                        PirAgProbeYLimitPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        cur=statusDict.get(PirAgProbeYLimitPlugin.aliases[0])
        cmd=statusDict.get(PirAgProbeYLimitPlugin.aliases[1])
        self.limit.update_limit(current=cur, cmd=cmd)
