import PlBase
import Telescope
from PyQt4 import QtGui, QtCore

class TelescopePlugin(PlBase.Plugin):
    """ Telescope """
    aliases=['TSCV.DomeShutter', 'TSCV.TopScreen', 'TSCL.TSFPOS', \
             'TSCL.TSRPOS', 'TSCV.WINDSDRV', 'TSCV.WindScreen', \
             'TSCL.WINDSPOS', 'TSCL.WINDSCMD', 'TSCL.WINDD', 'TSCL.Z', \
             'TSCV.FOCUSINFO', 'TSCV.FOCUSINFO2', 'TSCV.FOCUSALARM', \
             'TSCS.AZ', 'STATL.TELDRIVE', 'TSCS.EL', \
             'TSCV.M1Cover', 'TSCV.M1CoverOnway', 'TSCV.CellCover', \
             'TSCV.ADCONOFF_PF', 'TSCV.ADCMODE_PF', 'TSCV.ADCInOut',  \
             'TSCV.ADCOnOff', 'TSCV.ADCMode', 'TSCV.ADCInOut', \
             'TSCV.ImgRotRotation', 'TSCV.ImgRotMode', 'TSCV.ImgRotType', \
             'TSCV.INSROTROTATION_PF', 'TSCV.INSROTMODE_PF', \
             'TSCV.InsRotRotation', 'TSCV.InsRotMode', \
             'WAV.STG1_PS', 'WAV.STG2_PS', 'WAV.STG3_PS', \
             'TSCV.TT_Mode', 'TSCV.TT_Drive', 'TSCV.TT_DataAvail', \
             'TSCV.TT_ChopStat',]
  
    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()

        obcp=self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
        self.telescope=Telescope.Telescope(qtwidget, obcp=obcp, \
                                           logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.telescope,stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.controller.register_select('telescope', self.update, \
                                         TelescopePlugin.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            self.telescope.update_telescope(**statusDict) 
        except Exception as e:
            self.logger.error('error: updating status. %s' %str(e))
            

