#
# EnvMon.py -- Environment plugin for StatMon
# 
# Takeshi Inagaki (tinagaki@naoj.org)
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Fri Jun  8 14:56:15 HST 2012
#]
#
from __future__ import absolute_import
from __future__ import print_function
import time
import math
import os
import sys
import shelve

from qtpy import QtWidgets, QtCore

import Gen2.senvmon.statusGraph as StatusGraph
import Gen2.senvmon.timeValueGraph as timeValueGraph
# Needed for unpickling...ugh
from Gen2.senvmon.timeValueGraph import Global
from six.moves import range
# Hack required by timeValueGraph
timeValueGraph.Global.persistentData = {}

from g2base import ssdlog

windd_outside = "TSCL.WINDD"
windd_dome = "STATS.AZ_ADJ"
winds_outside = "TSCL.WINDS_O"
winds_dome = "TSCL.WINDS_I"
temp_outside = "TSCL.TEMP_O"
temp_dome = "TSCL.TEMP_I"
humi_outside = "TSCL.HUMI_O"
humi_dome = "TSCL.HUMI_I"
m1_temp = "TSCL.M1_TEMP"
dew_point = "STATL.DEW_POINT_O"
topring_f = "TSCL.TOPRING_WINDS_F"
topring_r = "TSCL.TOPRING_WINDS_R"

#test = "TSCL.SEEN"

def __set_data(envi_data, key, logger):

    try:
        Global.persistentData = envi_data[key]
        #print 'GETDATA:%d' % len(Global.persistentData['temperature'][0])
        #print 'GETDATA:%s' % Global.persistentData 
        logger.debug('getting data for key %s' %key)
        #print envi_data[key_str]
    #except KeyError as e:
    except Exception as e:
        Global.persistentData = {}
        logger.error('error: setting data. %s' %e)

def __restore_data(envi_data, key, logger):
    try:
        envi_data[key] = Global.persistentData
    except Exception as e:
        logger.error('error: restoring data. %s' %e)

def __remove_old_data(datapoint, logger):
 
    for k in Global.persistentData.keys():
         logger.debug('removing key=%s' %k)
         try:
             for val in range(len(Global.persistentData[k])):
                  num_points = len(Global.persistentData[k][val])
                  logger.debug('length of datapoint=%d' %num_points )
                  if num_points > datapoint:
                      del Global.persistentData[k][val][:num_points-datapoint]  
         except Exception as e:  
             logger.error('error: removing old data. %s' %e)

def load_data(data_file, datakey, datapoint, logger):
    ''' loading data '''

    # open/load shelve file 
    try:
        logger.debug('opening env data file %s...' % data_file)
        envi_data = shelve.open(data_file)
    except Exception as e:
        logger.error('error: opening envi file: %s, Error: %s' % (data_file, str(e)))
        Global.persistentData = {}
    else:
        __set_data(envi_data, datakey, logger)  
        __remove_old_data(datapoint, logger)
        __restore_data(envi_data, datakey, logger)
        envi_data.close()

progname = os.path.basename(sys.argv[0])


class EnvMon(QtWidgets.QWidget):

    def __init__(self, parent=None, obcp=None,  logger=None):
        super(EnvMon, self).__init__(parent)
        self.logger = logger

        self.statusDict = {}
        self.envi_file = None
        self.datakey = 'envmon'
        #self.data_file =  'envi.shelve'

        filename =  'envi.shelve'
        shelve_path = os.path.join(self._get_shelve_path(), filename)


        self.__load_data(shelve_path) 

        self.sc = timeValueGraph.TVCoordinator(self.statusDict, 10, \
                      shelve_path, self.datakey, self.logger)

        self.widgets = []
        # wind direction
        self.wd = StatusGraph.StatusGraph(title="Wind Dir N:0 E:90",
                                    key="winddir",
                                    statusKeys=(windd_outside, windd_dome),
                                    statusFormats=("Outside: %0.1f", "Dome: %0.1f"),
                                    maxDeltas=(300, 300),
                                    logger=self.logger)
        # don't crop/scale the compass values to the wind data
        self.wd.hardMinDisplayVal = -0.1
        self.wd.hardMaxDisplayVal = 370
        self.wd.valueRulerRight.marksPerUnit = 1
        self.wd.valueRulerRight.hardValueIncrement = 90
        self.wd.valueRulerLeft.marksPerUnit = 1
        self.wd.valueRulerLeft.hardValueIncrement = 90


        
        self.widgets.append(self.wd)

        # wind speed
        self.ws = StatusGraph.StatusGraph(title="Wind Speed (m/s)",
                             key="windspeed",
                             statusKeys=(winds_outside, winds_dome),
                             alarmValues = (19.9,10),
                             warningValues = (7,5),
                             ruler='LR',
                             logger=self.logger)

        self.widgets.append(self.ws) 
        # temperature
        self.temp = StatusGraph.StatusGraph(title="Temperature (C)",
                             key="temperature",
                             statusKeys=(temp_outside, temp_dome),
                             displayTime=True,
                             ruler='LR',
                             logger=self.logger)
    
        self.widgets.append(self.temp)

        # humidity
        self.h = StatusGraph.StatusGraph(title="Humidity (%)",
                             key="humidity",
                             statusKeys=(humi_outside, humi_dome),
                             alarmValues = (80,80),
                             warningValues = (70,70),
                             ruler='LR',            
                             logger=self.logger)
        self.widgets.append(self.h)

        # m1 temperature and dew point(outside)
        self.md = StatusGraph.StatusGraph(title="M1 & Dew (C)",
                             key="m1dew",
                             statusKeys=(m1_temp, dew_point),
                             statusFormats=("M1: %0.2f", "Dew: %0.2f"),
#                             alarmValues = (5,5),
                             ruler='LR',
                             logger=self.logger)
        self.widgets.append(self.md)
 
        # top ring(front & rear) wind speed 
        self.topring = StatusGraph.StatusGraph(title="TopRing WindSpeed",
                             key="topring",
                             statusKeys=(topring_f, topring_r),
                             statusFormats=("Front: %0.2f", "Rear: %0.2f"),
                             alarmValues = (2,2),
                             displayTime=True,
                             ruler='LR',
                             logger=self.logger)
        self.widgets.append(self.topring)

        # # M1 temperature 
        # self.m1 = StatusGraph.StatusGraph(title="M1 Temp (C)",
        #                      key="m1temp",
        #                      statusKeys=(m1_temp,),
        #                      statusFormats=("%0.2f",),
        #                      alarmValues = (5,5),
        #                      logger=self.logger)

        # # Dew Point(outside)
        # self.dew = StatusGraph.StatusGraph(title="Dew Point (C)",
        #                      key="dewpoint",
        #                      statusKeys=(dew_point,),
        #                      statusFormats=("Outside: %0.2f",),
        #                      alarmValues = (5,5),
        #                      logger=self.logger)

        self.__set_layout()
 
    def _get_shelve_path(self):
        try:
            g2comm = os.environ['GEN2COMMON']
            path = os.path.join(g2comm, 'db')  
        except OSError as e:
            logger.error('error: %s' %e)
            path = os.path.join('/gen2/share/db')   

        return path
  

    def __load_data(self, shelve_path):

        datapoint=3600
        load_data(shelve_path, self.datakey, \
                  datapoint, logger=self.logger)

    def __set_layout(self):

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0) 
        layout.setContentsMargins(0, 0, 0, 0)

        for widget in self.widgets: 
            self.sc.addGraph(widget)
            layout.addWidget(widget, stretch=1)
        self.setLayout(layout)

    def start(self):
        now = time.time()
        self.sc.setTimeRange(now - (3600*4), now, calcTimeRange=True)
        self.sc.timerEvent(False)

    def update_envmon(self, status_dict):
        self.logger.debug('updating envmon. %s' %str(status_dict))
        self.statusDict.update(status_dict)
        try:
            self.sc.timerEvent(True)
        except Exception as e:
            self.logger.error("error: updating status: %s" % (str(e)))

    def tick(self):
        import random  
      
        windd = random.uniform(0, 360) 
        winds = random.uniform(0, 30)
        temp = random.uniform(-10, 20)
        humi = random.uniform(0, 100)

        statusDict = {windd_outside: windd, windd_dome: windd, \
                      winds_outside: winds, winds_dome: winds, \
                      temp_outside: temp, temp_dome: temp, \
                      humi_outside: humi, humi_dome: humi,\
                      m1_temp: temp, dew_point: temp, \
                      topring_f: winds, topring_r: winds}

        self.update_envmon(statusDict)

def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=450; self.h=550;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            em = EnvMon(parent=self.main_widget, logger=logger)
            l.addWidget(em)
            em.start()
            timer = QtCore.QTimer(self)
            timer.timeout.connect(em.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("starting...")

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtWidgets.QApplication(sys.argv)
        aw = AppWindow()
        print('state')
        #state = State(logger=logger)  
        aw.setWindowTitle("%s" % progname)
        aw.show()
        #state.show()
        print('show')
        sys.exit(qApp.exec_())

    except KeyboardInterrupt as e:
        logger.warn('keyboard interruption....')
        sys.exit(0)



if __name__ == '__main__':
    # Create the base frame for the widgets

    from optparse import OptionParser
 
    usage = "usage: %prog [options] command [args]"
    optprs = OptionParser(usage=usage, version=('%%prog'))
    
    optprs.add_option("--debug", dest="debug", default=False, action="store_true",
                      help="Enter the pdb debugger on main()")
    optprs.add_option("--display", dest="display", metavar="HOST:N",
                      help="Use X display on HOST:N")
    optprs.add_option("--profile", dest="profile", action="store_true",
                      default=False,
                      help="Run the profiler on main()")
    optprs.add_option("--interval", dest="interval", type='int',
                      default=1000,
                      help="Inverval for plotting(milli sec).")

    ssdlog.addlogopts(optprs)
    
    (options, args) = optprs.parse_args()

    if len(args) != 0:
        optprs.error("incorrect number of arguments")

    if options.display:
        os.environ['DISPLAY'] = options.display

    # Are we debugging this?
    if options.debug:
        import pdb

        pdb.run('main(options, args)')

    # Are we profiling this?
    elif options.profile:
        import profile

        print("%s profile:" % sys.argv[0])
        profile.run('main(options, args)')

    else:
        main(options, args)

    
#END
