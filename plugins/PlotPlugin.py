#
# Takeshi Inagaki
# Eric Jeschke (eric@naoj.org)
#
import PlBase
import Plot
from PyQt4 import QtGui, QtCore

class AgPlotPlugin(PlBase.Plugin):
    """ AG Plotting """
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.ag=Plot.AgPlot(qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.ag,stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.aliases=['STATL.TELDRIVE', 'TSCL.AG1dX', 'TSCL.AG1dY', 
                      'TSCV.AGExpTime', 'TSCV.AG1_I_BOTTOM', 'TSCV.AG1_I_CEIL',
                      ]
#        self.logger.debug('start aliases=%s' %self.aliases)
        self.controller.register_select('agplot', self.update, self.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        #status={'TSCL.AG1dY': 2000, 'TSCL.AG1dX': 3000}
        state = statusDict.get(self.aliases[0])
        x = statusDict.get(self.aliases[1])
        y = statusDict.get(self.aliases[2])
        exp = statusDict.get(self.aliases[3])
        bottom = statusDict.get(self.aliases[4])
        ceil = statusDict.get(self.aliases[5]) 
        self.ag.update_plot(state=state, x=x, y=y, \
                            exptime=exp, bottom=bottom, ceil=ceil)


class TwoGuidingPlotPlugin(PlBase.Plugin):
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.plot = Plot.TwoGuidingPlot(qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        layout.addWidget(self.plot, stretch=1)
        container.setLayout(layout)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        state = statusDict.get(self.aliases[0])
        guiding1_x = statusDict.get(self.aliases[1])
        guiding1_y = statusDict.get(self.aliases[2])
        guiding2_x = statusDict.get(self.aliases[3])
        guiding2_y = statusDict.get(self.aliases[4])
        guiding1_exp = statusDict.get(self.aliases[5])
        guiding2_exp = statusDict.get(self.aliases[6])
        guiding1_bottom = statusDict.get(self.aliases[7])
        guiding1_ceil = statusDict.get(self.aliases[8])
        guiding2_bottom = statusDict.get(self.aliases[9])
        guiding2_ceil = statusDict.get(self.aliases[10])

        self.plot.update_plot(state, guiding1_x, guiding1_y, guiding2_x, guiding2_y, \
                               guiding1_exp, guiding2_exp, \
                               guiding1_bottom, guiding1_ceil, \
                               guiding2_bottom, guiding2_ceil)


class NsOptPlotPlugin(TwoGuidingPlotPlugin):
    """ Ns-Opt AG/SV Plotting """
  
    def start(self):
        self.aliases=['STATL.TELDRIVE', \
                      'TSCL.AG1dX', 'TSCL.AG1dY', \
                      'TSCL.SV1DX', 'TSCL.SV1DY', \
                      'TSCV.AGExpTime', 'TSCV.SVExpTime',\
                      'TSCV.AG1_I_BOTTOM', 'TSCV.AG1_I_CEIL', \
                      'TSCV.SV1_I_BOTTOM', 'TSCV.SV1_I_CEIL']
        self.controller.register_select('nsoptplot', self.update, self.aliases)


class HscPlotPlugin(TwoGuidingPlotPlugin):
    """ Hsc SC/SHAG Plotting """
  
    def start(self):

        self.aliases=['STATL.TELDRIVE', \
                      'TSCL.HSC.SCAG.DX', 'TSCL.HSC.SCAG.DY', \
                      'TSCL.HSC.SHAG.DX', 'TSCL.HSC.SHAG.DY', \
                      'TSCV.HSC.SCAG.ExpTime', 'TSCV.HSC.SHAG.ExpTime', \
                      'TSCV.HSC.SCAG.I_BOTTOM', 'TSCV.HSC.SCAG.I_CEIL', \
                      'TSCV.HSC.SHAG.I_BOTTOM', 'TSCV.HSC.SHAG.I_CEIL']
        self.controller.register_select('hscplot', self.update, self.aliases)


class FmosPlotPlugin(PlBase.Plugin):
    """ FMOS Plotting """
    aliases=['STATL.TELDRIVE', 'TSCL.AGFMOSdAZ', 'TSCL.AGFMOSdEL', 'TSCS.EL']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.fmos=Plot.FmosPlot(qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        layout.addWidget(self.fmos,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %self.aliases)
        self.controller.register_select('fmosplot', self.update, FmosPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        state=statusDict.get(FmosPlotPlugin.aliases[0])
        x=statusDict.get(FmosPlotPlugin.aliases[1])
        y=statusDict.get(FmosPlotPlugin.aliases[2])
        el=statusDict.get(FmosPlotPlugin.aliases[3])
        self.fmos.update_plot(state, x, y, el)


class NsIrPlotPlugin(PlBase.Plugin):
    """ AO188 Plotting """
    aliases=['AON.TT.TTX','AON.TT.TTY', 'AON.TT.WTTC1','AON.TT.WTTC2']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.nsir=Plot.NsIrPlot(qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        layout.addWidget(self.nsir,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %self.aliases)
        self.controller.register_select('nsirplot', self.update, NsIrPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        ao1x=statusDict.get(NsIrPlotPlugin.aliases[0])
        ao1y=statusDict.get(NsIrPlotPlugin.aliases[1])
        ao2x=statusDict.get(NsIrPlotPlugin.aliases[2])
        ao2y=statusDict.get(NsIrPlotPlugin.aliases[3])
        self.nsir.update_plot(ao1x, ao1y, ao2x, ao2y)


# not used. commented out
# class PirPlotPlugin(PlBase.Plugin):
#     """ PIR Plotting """
#     aliases=['TSCL.AGPIRdX', 'TSCL.AGPIRdY']
  
#     def build_gui(self, container):
#         self.root = container

#         qtwidget = QtGui.QWidget()
#         self.pir=Plot.Plot(qtwidget, logger=self.logger)
       
#         layout = QtGui.QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0) 
#         layout.addWidget(self.pir,stretch=1)
#         container.setLayout(layout)
 
#     def start(self):
# #        self.logger.debug('start aliases=%s' %self.aliases)
#         self.controller.register_select('pirplot', self.update, PirPlotPlugin.aliases)

#     def update(self, statusDict):
#         self.logger.debug('status=%s' %str(statusDict))
#         x=statusDict.get(PirPlotPlugin.aliases[0])
#         y=statusDict.get(PirPlotPlugin.aliases[1])
#         self.pir.update_plot(x, y)



