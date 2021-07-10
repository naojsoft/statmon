from qtpy import QtWidgets, QtCore
import sip

import PlBase
from StatusTable import StatusTable
import Telescope
from g2cam.INS import INSdata


class StatusTablePlugin(PlBase.Plugin):
    """ StatusTable Plugin"""


    def set_layout(self):

        qtwidget = QtWidgets.QWidget()

        self.statustable = StatusTable(parent=qtwidget, logger=self.logger)

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)
        self.vlayout.addWidget(self.statustable, stretch=1)
        self.root.setLayout(self.vlayout)

    def set_obcp_alias(self, inscode):

        self.aliases = ['FITS.SBR.MAINOBCP', \
                        'GEN2.STATUS.TBLTIME.{0}S0001'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0002'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0003'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0004'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0005'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0006'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0007'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0008'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.{0}S0009'.format(inscode), \
                        'GEN2.STATUS.TBLTIME.TSCS', 'GEN2.STATUS.TBLTIME.TSCL', 'GEN2.STATUS.TBLTIME.TSCV']

        self.logger.info('aliases=%s' %self.aliases)

    def obcp_alias(self, obcp):

        insdata = INSdata()

        try:
            inscode = insdata.getCodeByName(obcp)
        except Exception as e:
            self.logger.error('error: fail to fetch inscode.  %s' %e)
            inscode = None

        return inscode


    def build_gui(self, container):

        self.root = container

        try:
            self.obcp = self.controller.proxystatus.fetchOne('FITS.SBR.MAINOBCP')
        except Exception as e:
            self.logger.error('error: building layout. %s' %e)
        else:
            inscode = self.obcp_alias(self.obcp)
            self.logger.info('inscode=%s' %inscode)
            self.set_obcp_alias(inscode)
            self.set_layout()

    def start(self):
        self.controller.register_select('statustable', self.update, \
                                         self.aliases)
        #self.controller.add_callback('change-config', self.change_config)

    def update_obcp(self, obcp):

        inscode = self.obcp_alias(obcp)
        self.set_obcp_alias(inscode)
        self.obcp = obcp
        self.start()
        return obcp

    def update(self, statusDict):
        self.logger.info('status=%s' %str(statusDict))
        obcp = statusDict.get(self.aliases[0])
        if not self.obcp == obcp:
            obcp = self.update_obcp(obcp)

        obcp_time1 = statusDict.get(self.aliases[1])
        obcp_time2 = statusDict.get(self.aliases[2])
        obcp_time3 = statusDict.get(self.aliases[3])
        obcp_time4 = statusDict.get(self.aliases[4])
        obcp_time5 = statusDict.get(self.aliases[5])
        obcp_time6 = statusDict.get(self.aliases[6])
        obcp_time7 = statusDict.get(self.aliases[7])
        obcp_time8 = statusDict.get(self.aliases[8])
        obcp_time9 = statusDict.get(self.aliases[9])

        self.logger.debug('obcp_time1=%s obcp_time2=%s  obcp_time3=%s obcp_time4=%s obcp_time5=%s obcp_time6=%s obcp_time7=%s obcp_time8=%s obcp_time9=%s' %(obcp_time1, obcp_time2, obcp_time3, obcp_time4, obcp_time5, obcp_time6, obcp_time7, obcp_time8, obcp_time9 ))


        tscs_time = statusDict.get(self.aliases[10])
        tscl_time = statusDict.get(self.aliases[11])
        tscv_time = statusDict.get(self.aliases[12])
        mon_time = self.controller.last_update

        self.logger.info('mon last_update=%s' %str(mon_time))

        self.statustable.update_statustable(obcp=obcp, obcp_time1=obcp_time1, obcp_time2=obcp_time2, \
                                            obcp_time3=obcp_time3, obcp_time4=obcp_time4, \
                                            obcp_time5=obcp_time5, obcp_time6=obcp_time6, \
                                            obcp_time7=obcp_time7, obcp_time8=obcp_time8, \
                                            obcp_time9=obcp_time9, \
                                            tscs_time=tscs_time, tscl_time=tscl_time, \
                                            tscv_time=tscv_time, mon_time=mon_time)
