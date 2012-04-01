#!/usr/bin/env python
#
# statmon.py -- Flexible Gen2 status monitor.
#
#[ Eric Jeschke (eric@naoj.org) --
#  Last edit: Fri Mar 30 17:27:25 HST 2012
#]
#
"""
Usage:
    statmon.py 
"""

# stdlib imports
import sys, os
import threading
import ssdlog

moduleHome = os.path.split(sys.modules[__name__].__file__)[0]
sys.path.insert(0, moduleHome)
widgetHome = os.path.join(moduleHome, 'view')
sys.path.insert(0, widgetHome)

# Subaru python stdlib imports
import remoteObjects as ro
import remoteObjects.Monitor as Monitor
import Gen2.soundsink as SoundSink
import ModuleManager
import Settings

# Local application imports
import Model
## import View
## import Control

defaultServiceName = 'statmon'
version = "20120329.0"

default_layout = ['hpanel', {},
                  ['ws', dict(name='left', width=280),
                   # (tabname, layout), ...
                   [("Info", ['vpanel', {},
                              ['ws', dict(name='uleft', height=280,
                                          show_tabs=False)],
                              ['ws', dict(name='lleft', show_tabs=False)],
                              ]
                     )]
                     ],
                  ['vbox', dict(name='main', width=700)],
                  ['ws', dict(name='right', width=400),
                   # (tabname, layout), ...
                   [("Dialogs", ['ws', dict(name='dialogs')
                                 ]
                     )]
                    ],
                  ]


def foo(d):
    print "callback got:", d
    
def main(options, args):
    # Create top level logger.
    svcname = options.svcname
    logger = ssdlog.make_logger(svcname, options)

    # Initialize remote objects subsystem.
    try:
        ro.init()

    except ro.remoteObjectError, e:
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
    if os.environ.has_key('CONFHOME'):
        basedir = os.path.join(os.environ['CONFHOME'], svcname)
    else:
        basedir = os.path.join(os.environ['HOME'], '.' + svcname)
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    settings = Settings.Settings(basefolder=basedir)

    mm = ModuleManager.ModuleManager(logger)

    model = Model.StatusModel(logger)
    model.register_select('foo', foo, ['FOO.BAR'])
    
    ## # Start up the display engine
    ## viewer = Viewer.Viewer(logger, threadPool, mm, settings,
    ##                         sndsink, ev_quit)

    ## # Build desired layout
    ## viewer.build_toplevel(layout=default_layout)

    ## # Add any custom plugins
    ## if options.plugins:
    ##     plugins = options.plugins.split(',')
    ##     for plname in plugins:
    ##         viewer.add_local_plugin(plname)

    ## viewer.update_pending()

    ## controller = Controller(viewer, mymon, logger)

    # Did user specify geometry
    ## if options.geometry:
    ##     viewer.setGeometry(options.geometry)

    server_started = False

    # Create receiver and start it
    try:
        # Startup monitor threadpool
        mymon.start(wait=True)

        # start_server is necessary if we are subscribing, but not if only
        # publishing
        mymon.start_server(wait=True, port=options.monport)
        server_started = True

        if options.monitor:
            # subscribe our monitor to the central monitor hub
            mymon.subscribe_remote(options.monitor, channels, {})
            # publishing for remote command executions
            mymon.publish_to(options.monitor, ['sound'], {})

        # Register local status info subscription callback
        mymon.subscribe_cb(model.arr_status, ['status'])

        ## # Create our remote service object
        ## ctrlsvc = ro.remoteObjectServer(svcname=options.svcname,
        ##                                 obj=controller,
        ##                                 logger=logger, ev_quit=ev_quit,
        ##                                 port=options.port,
        ##                                 usethread=True,
        ##                                 threadPool=threadPool)

        logger.info("Starting statmon service.")
        ## ctrlsvc.ro_start()

        try:
            # Main loop to handle GUI events
            #viewer.mainloop(timeout=0.001)
            while True:
                ev_quit.wait(1.0)

        except KeyboardInterrupt:
            logger.error("Received keyboard interrupt!")

    finally:
        logger.info("Shutting down...")

        ## viewer.stop()
        ## ctrlsvc.ro_stop(wait=True)
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
    ssdlog.addlogopts(optprs)

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

        print "%s profile:" % sys.argv[0]
        profile.run('main(options, args)')


    else:
        main(options, args)

# END
