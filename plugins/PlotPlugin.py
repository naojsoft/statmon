import PlBase
import Plot
from PyQt4 import QtGui, QtCore

class AgPlotPlugin(PlBase.Plugin):
    """ AG Plotting """
    aliases=['STATL.TELDRIVE', 'TSCL.AG1dX', 'TSCL.AG1dY', \
             'TSCV.AGExpTime', 'TSCV.AG1_I_BOTTOM', 'TSCV.AG1_I_CEIL']
  
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
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('agplot', self.update, AgPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        #status={'TSCL.AG1dY': 2000, 'TSCL.AG1dX': 3000}
        state = statusDict.get(AgPlotPlugin.aliases[0])
        x = statusDict.get(AgPlotPlugin.aliases[1])
        y = statusDict.get(AgPlotPlugin.aliases[2])
        exp = statusDict.get(AgPlotPlugin.aliases[3])
        bottom = statusDict.get(AgPlotPlugin.aliases[4])
        ceil = statusDict.get(AgPlotPlugin.aliases[5]) 
        self.ag.update_plot(state=state, x=x, y=y, \
                            exptime=exp, bottom=bottom, ceil=ceil)


class NsOptPlotPlugin(PlBase.Plugin):
    """ SV Plotting """
    aliases=['STATL.TELDRIVE', 'TSCL.AG1dX', 'TSCL.AG1dY', \
             'TSCL.SV1DX', 'TSCL.SV1DY', \
             'TSCV.AGExpTime', 'TSCV.SVExpTime',\
             'TSCV.AG1_I_BOTTOM', 'TSCV.AG1_I_CEIL', \
             'TSCV.SV1_I_BOTTOM', 'TSCV.SV1_I_CEIL']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.nsopt=Plot.NsOptPlot(qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        layout.addWidget(self.nsopt,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('nsoptplot', self.update, NsOptPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        state = statusDict.get(NsOptPlotPlugin.aliases[0])
        ag_x = statusDict.get(NsOptPlotPlugin.aliases[1])
        ag_y = statusDict.get(NsOptPlotPlugin.aliases[2])
        sv_x = statusDict.get(NsOptPlotPlugin.aliases[3])
        sv_y = statusDict.get(NsOptPlotPlugin.aliases[4])
        ag_exp = statusDict.get(NsOptPlotPlugin.aliases[5])
        sv_exp = statusDict.get(NsOptPlotPlugin.aliases[6])
        ag_bottom = statusDict.get(NsOptPlotPlugin.aliases[7])
        ag_ceil = statusDict.get(NsOptPlotPlugin.aliases[8])
        sv_bottom = statusDict.get(NsOptPlotPlugin.aliases[9])
        sv_ceil = statusDict.get(NsOptPlotPlugin.aliases[10])

        self.nsopt.update_plot(state=state, ag_x=ag_x, ag_y=ag_y, \
                               sv_x=sv_x, sv_y=sv_y, \
                               ag_exp=ag_exp, sv_exp=sv_exp, \
                               ag_bottom=ag_bottom, ag_ceil=ag_ceil,\
                               sv_bottom=sv_bottom, sv_ceil=sv_ceil)


class PirPlotPlugin(PlBase.Plugin):
    """ PIR Plotting """
    aliases=['TSCL.AGPIRdX', 'TSCL.AGPIRdY']
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()
        self.pir=Plot.Plot(qtwidget, logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        layout.addWidget(self.pir,stretch=1)
        container.setLayout(layout)
 
    def start(self):
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('pirplot', self.update, PirPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        x=statusDict.get(PirPlotPlugin.aliases[0])
        y=statusDict.get(PirPlotPlugin.aliases[1])
        self.pir.update_plot(x, y)


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
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('fmosplot', self.update, FmosPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        state=statusDict.get(FmosPlotPlugin.aliases[0])
        x=statusDict.get(FmosPlotPlugin.aliases[1])
        y=statusDict.get(FmosPlotPlugin.aliases[2])
        el=statusDict.get(FmosPlotPlugin.aliases[3])
        self.fmos.update_plot(state, x, y, el)


class NsIrPlotPlugin(PlBase.Plugin):
    """ AO188-1 Plotting """
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
#        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
        self.controller.register_select('nsirplot', self.update, NsIrPlotPlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        ao1x=statusDict.get(NsIrPlotPlugin.aliases[0])
        ao1y=statusDict.get(NsIrPlotPlugin.aliases[1])
        ao2x=statusDict.get(NsIrPlotPlugin.aliases[2])
        ao2y=statusDict.get(NsIrPlotPlugin.aliases[3])
        self.nsir.update_plot(ao1x, ao1y, ao2x, ao2y)


 
# class AoPlotPlugin2(PlBase.Plugin):
#     """ AO188-2 Plotting """
#     aliases=['AON.TT.WTTC1','AON.TT.WTTC2']
  
#     def build_gui(self, container):
#         self.root = container

#         qtwidget = QtGui.QWidget()
#         self.ao2=Plot.AOPlot2(qtwidget, center_x=5.0, center_y=5.0, logger=self.logger)
       
#         layout = QtGui.QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0) 
#         layout.addWidget(self.ao2,stretch=1)
#         container.setLayout(layout)
 
#     def start(self):
# #        self.logger.debug('start aliases=%s' %AgPlotPlugin.aliases)
#         self.controller.register_select('aoplot2', self.update, AoPlotPlugin2.aliases)

#     def update(self, statusDict):
#         self.logger.debug('status=%s' %str(statusDict))
#         try: 
#             x=statusDict[AoPlotPlugin2.aliases[0]]
#             y=statusDict[AoPlotPlugin2.aliases[1]]
#         except Exception as e:
#             self.logger.error('error: ao2 x,y. %s' %e)
#         else:
#             self.ao2.update_plot(x, y)
