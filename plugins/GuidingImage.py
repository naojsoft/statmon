#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import time
import math
import os
import sys

# TODO: I think eventually most of these should be migrated over to
# statmon, or else redone....EJ
import Gen2.senvmon.statusGraph as StatusGraph
import Gen2.senvmon.timeValueGraph as timeValueGraph
# Needed for unpickling...ugh
from Gen2.senvmon.timeValueGraph import Global
import Gen2.senvmon.TVData as TVData
# Hack required by timeValueGraph
timeValueGraph.Global.persistentData = {}

from qtpy import QtWidgets, QtCore
#from Gen2.Fitsview.qtw import QtHelp

from g2base import ssdlog
from EnvMon import load_data

progname = os.path.basename(sys.argv[0])

ag_bright = 'TSCL.AG1Intensity'
sv_bright = 'TSCL.SV1Intensity'
fmos_bright = 'TSCL.AGFMOSIntensity'
ag_seeing = 'VGWD.FWHM.AG'
sv_seeing = 'VGWD.FWHM.SV'
fmos_seeing = 'TSCL.AGFMOSStarSize'

scag_bright = 'TSCL.HSC.SCAG.Intensity'
scag_seeing = 'TSCL.HSC.SCAG.StarSize'

shag_bright = 'TSCL.HSC.SHAG.Intensity'
shag_seeing = 'TSCL.HSC.SHAG.StarSize'


class GuidingImage(QtWidgets.QWidget):

    def __init__(self, parent=None, obcp=None,  logger=None):
        super(GuidingImage, self).__init__(parent)
        self.logger = logger

        self.statusDict = {}
        self.datakey = 'guidingimage'

        filename =  'guidingimage.pickle'
        persist_file_path = os.path.join(self._get_persist_file_path(), filename)

        bright, bright_format = self.__status_bright_format(obcp)
        seeing, seeing_format = self.__status_seeing_format(obcp) 

        self.__load_data(persist_file_path)

        self.sc = timeValueGraph.TVCoordinator(self.statusDict, 10, \
                                               persist_file_path, self.datakey, self.logger)

        self.bright = StatusGraph.StatusGraph(title="Brightness",
                          key='brightness',
                          size=(350, 200),
                          statusKeys=bright,
                          statusFormats=bright_format,
                          alarmValues = (999999, 999999),
#                      warningValues = (0,0),
                          displayTime=False,
                          ruler='LR',
                          #backgroundColor=QtWidgets.QColor(255,255,255),
                          logger=self.logger)

        self.seeing = StatusGraph.StatusGraph(title="Seeing",
                          key="seeingsize",
                          statusKeys=seeing,
                          alarmValues = (1,1),
                          statusFormats=seeing_format,
                          size=(350,200),
                          displayTime=True,
                          ruler='lr',
                          logger=self.logger)

        self.__set_layout()


    def _get_persist_file_path(self):
        try:
            g2comm = os.environ['GEN2COMMON']
            path = os.path.join(g2comm, 'db')  
        except OSError as e:
            logger.error('error: %s' %e)
            path = os.path.join('/gen2/share/db')   

        # If we don't have write access to the "path" directory, use
        # our home directory instead.
        if not os.access(path, os.W_OK):
            path = os.environ['HOME']

        return path
  

    def __load_data(self, persist_file_path):

        datapoint=86400
        load_data(persist_file_path, self.datakey, \
                  datapoint, logger=self.logger)

    def __status_bright_format(self, obcp):

        # hsc bright 
        #TSCL.HSC.SCAG.Intensity
        #TSCL.HSC.SHAG.Intensity

        # TO DO HSC brightness
        format = ("AG: %0.0f",)
        if obcp == 'FMOS':
            bright = (fmos_bright,)
        elif obcp == 'HSC':
            bright = (scag_bright, shag_bright)
            format = ("SC: %0.0f", "SH: %0.0f")
        elif obcp == 'HDS':
            bright = (ag_bright, sv_bright)
            format = ("AG: %0.0f", "SV: %0.0f")
        else: 
            bright = (ag_bright,)

        return (bright, format)

    def __status_seeing_format(self, obcp):

        #seeing
        #TSCL.HSC.SCAG.StarSize
        #TSCL.HSC.SHAG.StarSize

        # TO DO HSC seeing
        format = ("AG: %0.1f",)
        if obcp == 'FMOS':
            seeing = (fmos_seeing,)
        elif obcp == 'HSC':
            seeing  = (scag_seeing, shag_seeing)
            format = ("SC: %0.1f", "SH: %0.1f")
        elif obcp == 'HDS':
            seeing = (ag_seeing, sv_seeing)
            format = ("AG: %0.1f", "SV: %0.1f")
        else: 
            seeing = (ag_seeing,)

        return (seeing, format)

    def __set_layout(self):

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0) 
        layout.setContentsMargins(0, 0, 0, 0)

        for w in [self.bright, self.seeing]:
        #for w in [self.bright]:
            self.sc.addGraph(w)
            layout.addWidget(w, stretch=1)
        self.setLayout(layout)

    def start(self):
        now = time.time()
        self.sc.setTimeRange(now - (3600*4), now, calcTimeRange=True)
        self.sc.timerEvent(False)

    def update_guidingimage(self, status_dict):
        self.logger.debug('updating guiding-image. %s' %str(status_dict))
        self.statusDict.update(status_dict)
        try:
            self.sc.timerEvent(True)
        except Exception as e:
            self.logger.error("error: updating status: %s" % (str(e)))

    def tick(self):
        import random  
      
        ab = random.randrange(100000, 200000)
        sb = random.randrange(100000, 200000)

        asi = random.uniform(0, 1.5) 
        ssi = random.uniform(0, 1.5)

        statusDict = {ag_bright:ab, fmos_bright: ab, sv_bright: sb, \
                      ag_seeing: asi, sv_seeing: ssi, fmos_seeing: asi, \
                      scag_bright: ab, scag_seeing: asi, \
                      shag_bright: ab, shag_seeing: asi,}

        self.update_guidingimage(statusDict)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('state', options)
 
    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=350; self.h=100;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            gi = GuidingImage(parent=self.main_widget, obcp=options.ins, logger=logger)
            l.addWidget(gi)
            gi.start()
            timer = QtCore.QTimer(self)
            timer.timeout.connect(gi.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget) 
            self.statusBar().showMessage("%s starting..." %options.ins, options.interval)

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
    # note: there are sv/pir plotting, but mode ag uses the same code.  
    optprs.add_option("--ins", dest="ins",
                      default='HDS',
                      help="Specify an instrument. e.g. SPCAM")

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
