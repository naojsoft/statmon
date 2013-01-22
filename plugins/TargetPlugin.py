import PlBase
import Target
from PyQt4 import QtGui, QtCore

import  cfg.INS as INS


class TargetPlugin(PlBase.Plugin):
    """ Target """
    # aliases=['FITS.{0}.PROP_ID'.format(self.ins_code), \
    #          'FITS.{0}.OBJECT'.format(self.ins_code), \
    #          'TSCL.INSROTPA_PF', 'STATS.ROTDIF_PF', \
    #          'TSCL.ImgRotPA', 'STATS.ROTDIF', \
    #          'TSCL.InsRotPA', 'TSCL.LIMIT_FLAG', \
    #          'TSCL.LIMIT_AZ', 'TSCL.LIMIT_EL_LOW', \
    #          'TSCL.LIMIT_EL_HIGH', 'TSCL.LIMIT_ROT', \
    #          'TSCV.PROBE_LINK', 'TSCV.FOCUSINFO', \
    #          'TSCV.FOCUSINFO2']
  
    def set_aliases(self, ins_code):

        self.aliases=['FITS.{0}.PROP_ID'.format(ins_code), \
                 'FITS.{0}.OBJECT'.format(ins_code), \
                 'TSCL.INSROTPA_PF', 'STATS.ROTDIF_PF', \
                 'TSCL.ImgRotPA', 'STATS.ROTDIF', \
                 'TSCL.InsRotPA', 'TSCL.LIMIT_FLAG', \
                 'TSCL.LIMIT_AZ', 'TSCL.LIMIT_EL_LOW', \
                 'TSCL.LIMIT_EL_HIGH', 'TSCL.LIMIT_ROT', \
                 'TSCV.PROBE_LINK', 'TSCV.FOCUSINFO', \
                 'TSCV.FOCUSINFO2', 'TSCS.EL']

    def build_gui(self, container):
        self.root = container

        qtwidget = QtGui.QWidget()

        ins = INS.INSdata()
        obcp=self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
        ins_code = ins.getCodeByName(obcp)
        self.set_aliases(ins_code)

        self.target=Target.Target(qtwidget, obcp=ins_code, \
                                  logger=self.logger)
       
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.target,stretch=1)
        container.setLayout(layout)
 
    def start(self):
        self.controller.register_select('target', self.update, \
                                         self.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        try:
            self.target.update_target(**statusDict) 
        except Exception as e:
            self.logger.error('error: updating status. %s' %str(e))
            

