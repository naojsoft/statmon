import PlBase
import State
from PyQt4 import QtGui, QtCore

class AgStatePlugin(PlBase.Plugin):
    """ AG State """
  
    def build_gui(self, container):
        self.root = container
        qtwidget = QtGui.QWidget()
        self.state = State.State(parent=qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.state,stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.aliases = ['STATL.TELDRIVE', 'TSCL.AG1Intensity', 'STATL.AGRERR']
        self.controller.register_select('agstate', self.update, self.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        state = statusDict.get(self.aliases[0])
        intensity = statusDict.get(self.aliases[1])
        valerr = statusDict.get(self.aliases[2])
        self.state.update_state(state=state, intensity=intensity, valerr=valerr)


class FmosStatePlugin(AgStatePlugin):
    """ FMOS State """

    def start(self):
        self.aliases = ['STATL.TELDRIVE', 'TSCL.AGFMOSIntensity', 'STATL.AGRERR']
        self.controller.register_select('fmosstate', self.update, self.aliases)


class NsOptStatePlugin(PlBase.Plugin):
    """ NsOpt State """
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.state = State.State(parent=qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.state,stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.aliases = ['STATL.TELDRIVE', 'TSCL.AG1Intensity', 'STATL.AGRERR', \
                        'TSCL.SV1Intensity', 'STATL.SVRERR']
        self.controller.register_select('nsoptstate', self.update, self.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        state = statusDict.get(self.aliases[0])
        intensity1 = statusDict.get(self.aliases[1])
        valerr1 = statusDict.get(self.aliases[2])
        intensity2 = statusDict.get(self.aliases[3])
        valerr2 = statusDict.get(self.aliases[4])

        guiding1 = ("Guiding(AG1)", "Guiding(AG2)", "Guiding(HSCSCAG)")
        guiding2 = ("Guiding(SV1)", "Guiding(SV2)", "Guiding(HSCSHAG)")

        if state in guiding2:
            intensity, valerr = intensity2, valerr2
        elif state in guiding1:
            intensity, valerr = intensity1, valerr1 
        else:  # if not guiding, intensity and valerr don't matter. 
            intensity = valerr = None              
        self.state.update_state(state=state, intensity=intensity, valerr=valerr)


class HscStatePlugin(NsOptStatePlugin):
    """ Hsc State """
 
    def start(self):
        self.aliases = ['STATL.TELDRIVE', 'TSCL.HSC.SCAG.Intensity', 'STATL.AGRERR', \
                        'TSCL.HSC.SHAG.Intensity', 'STATL.AGRERR']
        self.controller.register_select('hscstate', self.update, self.aliases)


# not used. commented out
# class PirStatePlugin(AgStatePlugin):
#     """ PIR State """
#     aliases=['STATL.TELDRIVE', 'TSCL.AGPIRIntensity', 'STATL.AGRERR']
   
#     def start(self):
#         self.aliases=['STATL.TELDRIVE', 'TSCL.AGPIRIntensity', 'STATL.AGRERR']
#         self.controller.register_select('pirstate', self.update, self.aliases)


