import PlBase
import State
from PyQt4 import QtGui, QtCore

class AgStatePlugin(PlBase.Plugin):
    """ AG State """
    aliases=['STATL.TELDRIVE', 'TSCL.AG1Intensity', 'STATL.AGRERR']
  
    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        self.state=State.State(parent=qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.state,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('agstate', self.update, AgStatePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            state=statusDict[AgStatePlugin.aliases[0]]
            intensity=statusDict[AgStatePlugin.aliases[1]]
            valerr=statusDict[AgStatePlugin.aliases[2]]
        except Exception as e:
            self.logger.error('error: ag state intensity, valerr. %s' %e)
        else:
            self.state.update_state(state=state, intensity=intensity, valerr=valerr)


class NsOptStatePlugin(PlBase.Plugin):
    """ NsOpt State """
    aliases=['STATL.TELDRIVE', 'TSCL.AG1Intensity', 'STATL.AGRERR', 'TSCL.SV1Intensity', 'STATL.SVRERR']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.state=State.State(parent=qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.state,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('nsoptstate', self.update, NsOptStatePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try: 
            state=statusDict[NsOptStatePlugin.aliases[0]]
            ag_intensity=statusDict[NsOptStatePlugin.aliases[1]]
            ag_valerr=statusDict[NsOptStatePlugin.aliases[2]]
            sv_intensity=statusDict[NsOptStatePlugin.aliases[3]]
            sv_valerr=statusDict[NsOptStatePlugin.aliases[4]]

        except Exception as e:
            self.logger.error('error: nsopt state. %s' %e)
        else:
            ag_guiding=("Guiding(AG)", "Guiding(AG1)", "Guiding(AG2)")
            sv_guiding=("Guiding(SV)", "Guiding(SV1)", "Guiding(SV2)")
            if state in sv_guiding:
                intensity, valerr = sv_intensity, sv_valerr
            elif state in ag_guiding:
                intensity, valerr = ag_intensity, ag_valerr 
            else:  # if not guiding, the values of intensity/valerr don't matter, so just pass 0's 
                intensity, valerr = 0,0              
            self.state.update_state(state=state, intensity=intensity, valerr=valerr)


class FmosStatePlugin(PlBase.Plugin):
    """ FMOS State """
    aliases=['STATL.TELDRIVE', 'TSCL.AGFMOSIntensity', 'STATL.AGRERR']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.state=State.State(parent=qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.state,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('fmosstate', self.update, FmosStatePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try: 
            state=statusDict[FmosStatePlugin.aliases[0]]
            intensity=statusDict[FmosStatePlugin.aliases[1]]
            valerr=statusDict[FmosStatePlugin.aliases[2]]
        except Exception as e:
            self.logger.error('error: ag state intensity, valerr. %s' %e)
        else:
            self.state.update_state(state=state, intensity=intensity, valerr=valerr)


class PirStatePlugin(PlBase.Plugin):
    """ PIR State """
    aliases=['STATL.TELDRIVE', 'TSCL.AGPIRIntensity', 'STATL.AGRERR']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.state=State.State(parent=qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.state,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('pirstate', self.update, PirStatePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try: 
            state=statusDict[PirStatePlugin.aliases[0]]
            intensity=statusDict[PirStatePlugin.aliases[1]]
            valerr=statusDict[PirStatePlugin.aliases[2]]
        except Exception as e:
            self.logger.error('error: ag state intensity, valerr. %s' %e)
        else:
            self.state.update_state(state=state, intensity=intensity, valerr=valerr)


