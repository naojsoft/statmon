#!/usr/bin/env python
#
# statmon.py -- Flexible Gen2 status monitor.
#
# Eric Jeschke (eric@naoj.org)
#
"""
Usage:
    statmon.py --monport=NNNNN --plugins=X,Y,Z
"""
# stdlib imports
import sys, os
import threading

from ginga.qtw import QtHelp
from qtpy import QtWidgets, QtCore

moduleHome = os.path.split(sys.modules[__name__].__file__)[0]
sys.path.insert(0, moduleHome)
pluginHome = os.path.join(moduleHome, 'plugins')
sys.path.insert(0, pluginHome)

from g2base.remoteObjects import remoteObjects as ro
from g2base.remoteObjects import Monitor

# Subaru python stdlib imports
import g2client.soundsink as SoundSink

from ginga import toolkit
toolkit.use('qt4')
from ginga.gw import Widgets
from ginga.misc import ModuleManager, Settings, log

# Local application imports
import Model
from View import Viewer
from Control import Controller

defaultServiceName = 'statmon'
version = "20120405.0"

default_layout = ['seq', {},
                  ['vbox', dict(name='toplvl', width=2400, height=1100),
                   ['hbox', dict(name='menubox', stretch=0)],
                   ['vbox', dict(stretch=1),
                    ['ws', dict(name='top', show_tabs=False,
                                height=120, stretch=0), ],
                    ['hbox', dict(height=1000, stretch=1, spacing=6),
                     #['ws', dict(name='left', width=400), ],
                     ['vbox', dict(width=300, spacing=4, stretch=0),
                      ['ws', dict(name='left1', height=75, stretch=0,
                                  show_tabs=False), ],
                      ['ws', dict(name='left2', height=350, stretch=0,
                                  show_tabs=False), ],
                      ['ws', dict(name='left3', height=280, stretch=3,
                                  show_tabs=False),],
                      ['ws', dict(name='left4', height=80, stretch=1,
                                  show_tabs=False),],
                      ['ws', dict(name='left5', height=80, stretch=1,
                                  show_tabs=False),],
                      #['ws', dict(name='left6', height=80, show_tabs=False),],
                      ],
                     ['vbox', dict(width=400, spacing=4, stretch=0),
                      ['ws', dict(name='middle11', height=500, stretch=0,
                                  show_tabs=False), ],
                      ['ws', dict(name='middle12', height=80, stretch=1,
                                  show_tabs=False), ],
                      ['ws', dict(name='middle13', height=80, stretch=1,
                                  show_tabs=False), ],
                      ['ws', dict(name='middle14', height=80, stretch=1,
                                  show_tabs=False), ],
                      ['ws', dict(name='middle15', height=80, stretch=0,
                                  show_tabs=False), ],
                      ['ws', dict(name='middle16', height=80, show_tabs=False), ],
                      ['ws', dict(name='middle17', height=80, show_tabs=False), ],
                      ],
                     ['hpanel', dict(stretch=1),
                      ['vbox', dict(width=350, spacing=4),
                       ['ws', dict(name='middle21', height=25, stretch=0,
                                   show_tabs=False), ],
                       ['ws', dict(name='middle22', height=150, stretch=0,
                                   show_tabs=False), ],
                       ['ws', dict(name='middle23', height=50, stretch=0,
                                   show_tabs=False), ],
                       ['ws', dict(name='middle24', height=25, stretch=0,
                                   show_tabs=False), ],
                       ['ws', dict(name='middle25', height=350, stretch=3,
                                   show_tabs=False), ],
                       ['ws', dict(name='middle26', height=120, stretch=1,
                                   show_tabs=False), ],
                      ],
                      ['vbox', dict(width=350, stretch=1),
                       ['ws', dict(name='right1', width=350), ],
                      ],
                      ['vbox', dict(width=350, spacing=4, stretch=1),
                       ['ws', dict(name='farright1', show_tabs=False), ],
                      ],
                     ]
                    ],
                    ['ws', dict(name='bottom', show_tabs=False,
                                height=50, stretch=0), ],
                    ],
                   ['hbox', dict(name='statusbox', stretch=0)],
                   ]
                  ]

plugins = [
    # pluginName, moduleName, className, workspaceName, tabName
    ('radec', 'RaDec', 'RaDec', 'top', ''),
    ('times', 'RaDec', 'Times', 'bottom', ''),
    ('envmon', 'EnvMon', 'EnvMon', 'right1', 'EnvMon'),
    ('statusable', 'StatusTablePlugin', 'StatusTablePlugin', 'right1', 'StatTable'),
    ('debug', 'Debug', 'Debug', 'right1', "Debug"),
    ('state', 'StatePlugin', 'StatePlugin', 'left1', ''),
    ('plot', 'PlotPlugin', 'PlotPlugin', 'left2', ''),
    ('guidingimage', 'GuidingImage', 'GuidingImage', 'left3','' ),
    ('probe1limit', 'LimitPlugin', 'Probe1LimitPlugin', 'left4','' ),
    ('probe2limit', 'LimitPlugin', 'Probe2LimitPlugin', 'left5','' ),
    ('telescope', 'TelescopePlugin', 'TelescopePlugin', 'middle11',''),
    ('azlimit', 'LimitPlugin', 'AzLimitPlugin', 'middle12', ''),
    ('ellimit', 'LimitPlugin', 'ElLimitPlugin', 'middle13', ''),
    ('rotlimit', 'LimitPlugin', 'RotLimitPlugin', 'middle14','' ),
    ('tsccontrol', 'TscControlPlugin', 'TscControlPlugin', 'middle15','' ),
    ('domeff', 'DomeffPlugin', 'DomeffPlugin', 'middle21', ''),
    ('cal', 'CalPlugin', 'CalPlugin', 'middle23', ''),
    ('calprobe', 'CalprobePlugin', 'CalprobePlugin', 'middle24', ''),
    ('target', 'TargetPlugin', 'TargetPlugin', 'middle22', ''),
    ('envmon2', 'EnvMon2', 'EnvMon2', 'middle26', ''),
    ('alarm', 'Alarm', 'Alarm', 'middle25', ''),
    ('envmon3', 'EnvMon3', 'EnvMon3', 'farright1', ''),
    ]

class StatMon(Controller, Viewer):

    def __init__(self, logger, threadPool, module_manager, settings,
                 soundsink, ev_quit, model):

        self.soundsink = soundsink

        Viewer.__init__(self, logger, ev_quit)
        Controller.__init__(self, logger, threadPool, module_manager,
                            settings, ev_quit, model)

    def play_soundfile(self, filepath, format=None, priority=20):
        self.soundsink.playFile(filepath, format=format,
                                priority=priority)

    def add_menus(self):
        menubar = QtWidgets.QMenuBar()
        self.w.menubox.add_widget(Widgets.wrap(menubar), stretch=0)

        # create a File pulldown menu, and add it to the menu bar
        filemenu = menubar.addMenu("File")

        sep = QtWidgets.QAction(menubar)
        sep.setSeparator(True)
        filemenu.addAction(sep)

        item = QtWidgets.QAction("Quit", menubar)
        item.triggered.connect(self.quit)
        filemenu.addAction(item)

        # create a Option pulldown menu, and add it to the menu bar
        ## optionmenu = menubar.addMenu("Option")

    def add_statusbar(self):
        self.w.status = QtWidgets.QStatusBar()
        self.w.statusbox.add_widget(Widgets.wrap(self.w.status), stretch=1)

def main(options, args):
    # Create top level logger.
    svcname = options.svcname
    logger = log.get_logger(svcname, options=options)

    # Initialize remote objects subsystem.
    try:
        ro.init()

    except ro.remoteObjectError as e:
        logger.error("Error initializing remote objects subsystem: %s" % \
                     str(e))
        sys.exit(1)

    ev_quit = threading.Event()

    # make a name for our monitor
    myMonName = '%s-%s-%d.mon' % (svcname, ro.get_myhost(short=True),
                                  options.monport)

    # monitor channels we are interested in
    channels = options.monchannels.split(',')

    # Create a local pub sub instance
    mymon = Monitor.Monitor(myMonName, logger,
                            numthreads=options.numthreads)

    threadPool = mymon.get_threadPool()

    sndsink = SoundSink.SoundSource(monitor=mymon, logger=logger,
                                    channels=['sound'])

    # Get settings folder
    if 'CONFHOME' in os.environ:
        basedir = os.path.join(os.environ['CONFHOME'], svcname)
    else:
        basedir = os.path.join(os.environ['HOME'], '.' + svcname)
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    prefs = Settings.Preferences(basefolder=basedir, logger=logger)

    mm = ModuleManager.ModuleManager(logger)

    # Add any custom modules
    if options.modules:
        modules = options.modules.split(',')
        for mdlname in modules:
            #self.mm.loadModule(name, pfx=pluginconfpfx)
            self.mm.loadModule(name)

    model = Model.StatusModel(logger)

    # Start up the control/display engine
    statmon = StatMon(logger, threadPool, mm, prefs,
                      sndsink, ev_quit, model)

    # Build desired layout
    statmon.build_toplevel(layout=default_layout)
    for w in statmon.ds.toplevels:
        w.show()

    for pluginName, moduleName, className, wsName, tabName in plugins:
        statmon.load_plugin(pluginName, moduleName, className,
                            wsName, tabName)

    statmon.update_pending()

    # Did user specify geometry
    if options.geometry:
        statmon.set_geometry(options.geometry)

    server_started = False

    # Create receiver and start it
    try:
        # Startup monitor threadpool
        mymon.start(wait=True)

        # start_server is necessary if we are subscribing, but not if only
        # publishing
        mymon.start_server(wait=True, port=options.monport)
        server_started = True

        # Compute the union of channels supplied on command-line with
        # channels registered by plugins
        allChannels = set(channels) | model.channels

        if options.monitor:
            # subscribe our monitor to the central monitor hub.
            # Monitor.subscribe_remote requires that the channels be
            # supplied as a Python list, so convert allChannels from a
            # set to a list when we supply it to Monitor.subscribe_remote.
            mymon.subscribe_remote(options.monitor, list(allChannels), {})
            # publishing for remote command executions
            mymon.publish_to(options.monitor, ['sound'], {})

        # Register channel subscription callback
        logger.info('subscribe to channels {}'.format(allChannels))
        mymon.subscribe_cb(model.arr_channel, allChannels)

        # Create our remote service object
        ctrlsvc = ro.remoteObjectServer(svcname=options.svcname,
                                        obj=statmon,
                                        method_list=['close_plugin',
                                                     'close_all_plugins'],
                                        logger=logger, ev_quit=ev_quit,
                                        port=options.port,
                                        usethread=True,
                                        threadPool=threadPool)

        logger.info("Starting statmon service.")
        ctrlsvc.ro_start()

        try:
            # Main loop to handle GUI events
            statmon.mainloop(timeout=0.001)

        except KeyboardInterrupt:
            logger.error("Received keyboard interrupt!")

    finally:
        logger.info("Shutting down...")

        statmon.close_all_plugins()
        statmon.stop()
        ctrlsvc.ro_stop(wait=True)
        mymon.stop_server(wait=True)
        mymon.stop(wait=True)

    sys.exit(0)


if __name__ == "__main__":

    # Parse command line options with nifty new optparse module
    from optparse import OptionParser

    usage = "usage: %prog [options] cmd [args]"
    optprs = OptionParser(usage=usage, version=('%%prog %s' % version))

    optprs.add_option("--debug", dest="debug", default=False, action="store_true",
                      help="Enter the pdb debugger on main()")
    optprs.add_option("--display", dest="display", metavar="HOST:N",
                      help="Use X display on HOST:N")
    optprs.add_option("-g", "--geometry", dest="geometry",
                      metavar="GEOM", default="+20+100",
                      help="X geometry for initial size and placement")
    optprs.add_option("--modules", dest="modules", metavar="NAMES",
                      help="Specify additional modules to load")
    optprs.add_option("--monitor", dest="monitor", metavar="NAME",
                      default='monitor',
                      help="Synchronize from monitor named NAME")
    optprs.add_option("--monchannels", dest="monchannels",
                      default='status', metavar="NAMES",
                      help="Specify monitor channels to subscribe to")
    optprs.add_option("--monport", dest="monport", type="int",
                      help="Register monitor using PORT", metavar="PORT")
    optprs.add_option("--numthreads", dest="numthreads", type="int",
                      default=30,
                      help="Start NUM threads in thread pool", metavar="NUM")
    optprs.add_option("--plugins", dest="plugins", metavar="NAMES",
                      help="Specify additional plugins to load")
    optprs.add_option("--port", dest="port", type="int", default=None,
                      help="Register using PORT", metavar="PORT")
    optprs.add_option("--profile", dest="profile", action="store_true",
                      default=False,
                      help="Run the profiler on main()")
    optprs.add_option("--svcname", dest="svcname", metavar="NAME",
                      default=defaultServiceName,
                      help="Register using NAME as service name")
    log.addlogopts(optprs)

    (options, args) = optprs.parse_args(sys.argv[1:])

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

# END
