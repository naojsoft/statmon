#
# EnvMon.py -- Environment plugin for StatMon
# 
# Takeshi Inagaki (tinagaki@naoj.org)
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Mon Apr 30 13:04:07 HST 2012
#]
#
import time
import math
import os

import PlBase
import Bunch
# TODO: I think eventually most of these should be migrated over to
# statmon, or else redone....EJ
import Gen2.senvmon.statusGraph as StatusGraph
import Gen2.senvmon.timeValueGraph as timeValueGraph
# Hack required by timeValueGraph
timeValueGraph.Global.persistentData = {}
import Gen2.senvmon.resourceMon as rmon
import Gen2.senvmon.direction as dr

from PyQt4 import QtGui, QtCore
from Gen2.Fitsview.qtw import QtHelp

al_windd = "TSCL.WINDD"
al_windsO = "TSCL.WINDS_O"
al_windsI = "TSCL.WINDS_I"
al_tempO = "TSCL.TEMP_O"
al_tempI = "TSCL.TEMP_I"
al_humiO = "TSCL.HUMI_O"
al_humiI = "TSCL.HUMI_I"
al_atom = "TSCL.ATOM"
al_rain = "TSCL.RAIN"
al_seen = "TSCL.SEEN"
al_fwhm = "VGWD.FWHM.AG"
al_az = "TSCS.AZ"
al_h2o = "TSCV.WATER"
al_oil = "TSCV.OIL"


class EnvMon(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        #self.root.setStyleSheet("QWidget { background: lightblue }")

        self.statusDict = {}

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        container.setLayout(layout)

        split = QtGui.QSplitter()
        split.setOrientation(QtCore.Qt.Vertical)
        ## split.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored,
        ##                                       QtGui.QSizePolicy.Ignored))
        
        #self.w = Bunch.Bunch()

        envi_file=os.path.join(os.environ['GEN2COMMON'], 'db', 'envi.shelve')  
        key='envi_key'

        self.sc = timeValueGraph.TVCoordinator(self.statusDict, 10, envi_file,
                                               key, self.logger)
        coordinator = self.sc

        vbox = QtHelp.VBox()

        w = StatusGraph.StatusGraph(title="Wind direction N:0 E:90",
                                    key="winddir",
                                    size=(430, 200),
                                    statusKeys=(al_windd,),
                                    maxDeltas=(300,),
                                    backgroundColor=QtGui.QColor(245,255,252),
                                    logger=self.logger)
        # don't crop/scale the compass values to the wind data
        w.hardMinDisplayVal = -0.1
        w.hardMaxDisplayVal = 370
        w.valueRuler.marksPerUnit = 1
        w.valueRuler.hardValueIncrement = 90
        #w.setCoordinator(self.sc)
        coordinator.addGraph(w)
        vbox.addWidget(w, stretch=1)

        # wind speed
        widget = StatusGraph.StatusGraph(title="Wind Speed (m/s)",
                             key="windspeed",
                             size=(430,120),
                             statusKeys=(al_windsO, al_windsI),
                             alarmValues = (10,15),
                             backgroundColor=QtGui.QColor(247,255,244),                   
                             displayTime=True,
                             logger=self.logger)
        coordinator.addGraph(widget)
        vbox.addWidget(widget, stretch=1)

        # temperature
        widget = StatusGraph.StatusGraph(title="Temperature (C)",
                             key="temperature",
                             statusKeys=(al_tempO, al_tempI),
                             #statusObj=status_obj,
                             logger=self.logger)
        coordinator.addGraph(widget)
        vbox.addWidget(widget, stretch=1)

        # humidity
        widget = StatusGraph.StatusGraph(title="Humidity (%)",
                             key="humidity",
                             statusKeys=(al_humiO, al_humiI),
                             alarmValues = (80,80),
                             warningValues = (70,70),
                             backgroundColor=QtGui.QColor(255,255,246),
                             size=(430,112),
                             displayTime=True,
                             logger=self.logger)
        coordinator.addGraph(widget)
        vbox.addWidget(widget, stretch=1)

        # air pressure
        widget = StatusGraph.StatusGraph(title="Air Pressure (hPa)",
                             key="airpressure",
                             #size=(430,97),
                             size=(430,150),
                             statusKeys=(al_atom,),
                             statusFormats=("%0.1f",),
                             logger=self.logger)
        coordinator.addGraph(widget)
        vbox.addWidget(widget, stretch=1)

        # rain gauge
        widget = StatusGraph.StatusGraph(title="Rain Gauge (mm/h)",
                             key="raingauge",
                             statusKeys=(al_rain,),
                             statusFormats=("%0.1f",),
                             alarmValues = (50,),
                             #size=(430,93),
                             size=(430,150),
                             backgroundColor=QtGui.QColor(244,244,244),
                             logger=self.logger)
        coordinator.addGraph(widget)
        vbox.addWidget(widget, stretch=1)

        # seeing size
        widget = StatusGraph.StatusGraph(title="Seeing Size (arcsec)",
                             key="seeingsize",
                             statusKeys=(al_seen, al_fwhm),
                             alarmValues = (1,1),
                             statusFormats=("TSC: %0.1f", "VGW: %0.1f"),
                             #size=(430,97),
                             size=(430,150),
                             displayTime=True,
                             logger=self.logger)
        coordinator.addGraph(widget)
        vbox.addWidget(widget, stretch=1)
        split.addWidget(vbox)

        hbox = QtHelp.HBox()

        # resource monitor
        rs = rmon.ResourceMonitor(statusKeys=(al_h2o, al_oil),
                                  logger=self.logger)
        coordinator.graphs.append(rs)
    
        # wind direction 
        wind_dir = dr.Directions(statusKeys=(al_az, al_windd, al_windsO),
                                 logger=self.logger)
        wind_dir.resize(180, 180)
        coordinator.graphs.append(wind_dir)

        hbox.addWidget(rs, stretch=0, alignment=QtCore.Qt.AlignLeft)
        hbox.addWidget(wind_dir, stretch=0, alignment=QtCore.Qt.AlignLeft)

        split.addWidget(hbox)
        #layout.addWidget(split, stretch=1, alignment=QtCore.Qt.AlignTop)
        layout.addWidget(split, stretch=1)
        

    def start(self):
        aliases = [ al_windd, al_windsO, al_windsI, al_tempO,
                    al_tempI, al_humiO, al_humiI, al_atom, al_rain,
                    al_seen, al_fwhm, al_az, al_h2o, al_oil ]
        self.controller.register_select('envmon', self.update, aliases)
        now = time.time()
        self.sc.setTimeRange(now - (3600*4), now, calcTimeRange=True)
        self.sc.timerEvent(False)

    def update(self, statusDict):
        self.statusDict.update(statusDict)
        try:
            self.sc.timerEvent(True)
        except Exception, e:
            self.logger.error("Error updating status: %s" % (str(e)))
            
    def __str__(self):
        return 'envmon'
    
#END
