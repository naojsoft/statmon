#
# EnvMon.py -- Environment plugin for StatMon
# 
# Takeshi Inagaki (tinagaki@naoj.org)
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Fri Jun  8 14:56:15 HST 2012
#]
#
import time
import math
import os
import sys
import shelve

from PyQt4 import QtGui, QtCore

import Gen2.senvmon.statusGraph as StatusGraph
import Gen2.senvmon.timeValueGraph as timeValueGraph
# Needed for unpickling...ugh
from Gen2.senvmon.timeValueGraph import Global
# Hack required by timeValueGraph
timeValueGraph.Global.persistentData = {}

import ssdlog

winds_max = "STATL.CSCT_WINDS_MAX"

def __set_data(envi_data, key, logger):

    try:
        Global.persistentData = envi_data[key]
        #print 'GETDATA:%d' % len(Global.persistentData['temperature'][0])
        #print 'GETDATA:%s' % Global.persistentData 
        logger.debug('getting data for key %s' %key)
        #print envi_data[key_str]
    except KeyError as e:
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
        logger.debug('opening env data...')   
        envi_data = shelve.open(data_file)
    except Exception as e:
        logger.error('error: opening envi file. %s' %str(e))
        Global.persistentData = {}
    else:
        __set_data(envi_data, datakey, logger)  
        __remove_old_data(datapoint, logger)
        __restore_data(envi_data, datakey, logger)
        envi_data.close()

progname = os.path.basename(sys.argv[0])


class EnvMon(QtGui.QWidget):

    def __init__(self, parent=None, obcp=None,  logger=None):
        super(EnvMon, self).__init__(parent)
        self.logger = logger

        self.statusDict = {}
        self.envi_file = None
        self.datakey = 'envmon2'
        self.data_file =  'envi2.shelve'

        self.__load_data() 

        self.sc = timeValueGraph.TVCoordinator(self.statusDict, 10, \
                      self.data_file, self.datakey, self.logger)

        self.widgets = []

        # winds speed Max Value at the center section
        self.ws = StatusGraph.StatusGraph(title="Wind Speed CenterSection",
                             key="windspeedmax",
                             statusKeys=(winds_max,),
                             statusFormats=("Max: %0.2f(m/s)",),
                             alarmValues = (2.0,2.0),
                             displayTime=True, 
                             logger=self.logger)

        self.widgets.append(self.ws) 

        self.__set_layout()
 
    def __load_data(self):

        datapoint=3600
        try:
            g2comm = os.environ['GEN2COMMON']
            self.data_file = os.path.join(g2comm, 'db', self.data_file)  
        except OSError as e:
            logger.error('error: %s' %e)
            self.data_file = '/gen2/share/db/%s' %self.data_file   
        finally:
            load_data(self.data_file, self.datakey, \
                      datapoint, logger=self.logger)

    def __set_layout(self):

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0) 
        layout.setMargin(0)

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

        wind_speed = random.uniform(-1, 5)

        statusDict = {winds_max: wind_speed}

        self.update_envmon(statusDict)

def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtGui.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w = 450
            self.h = 150;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtGui.QWidget()
            l = QtGui.QVBoxLayout(self.main_widget)
            l.setMargin(0) 
            l.setSpacing(0)
            em = EnvMon(parent=self.main_widget, logger=logger)
            l.addWidget(em)
            em.start()
            timer = QtCore.QTimer(self)
            QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), em.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("starting...")

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtGui.QApplication(sys.argv)
        aw = AppWindow()
        print 'state'
        #state = State(logger=logger)  
        aw.setWindowTitle("%s" % progname)
        aw.show()
        #state.show()
        print 'show'
        sys.exit(qApp.exec_())

    except KeyboardInterrupt, e:
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

        print "%s profile:" % sys.argv[0]
        profile.run('main(options, args)')

    else:
        main(options, args)

    
#END
