#
# Control.py -- Controller for StatMon.
#
# Eric Jeschke (eric@naoj.org)
#
# stdlib imports
import sys, os
import traceback
import time
import threading
import six
if six.PY2:
    import Queue
    import thread
else:
    import queue as Queue
    import _thread as thread

from g2base.remoteObjects import remoteObjects as ro

from ginga.misc import Bunch, Callback, Future, Task

class ControlError(Exception):
    """Exception for errors thrown in this module."""
    pass

class Controller(Callback.Callbacks):

    def __init__(self, logger, threadPool, module_manager, settings,
                 ev_quit, model):
        Callback.Callbacks.__init__(self)

        self.logger = logger
        self.threadPool = threadPool
        self.mm = module_manager
        self.settings = settings
        self.ev_quit = ev_quit
        self.model = model
        self.last_update = None

        # For callbacks
        for name in ['change-config', ]:
            self.enable_callback(name)

        self.gui_queue = Queue.Queue()
        self.gui_thread_id = thread.get_ident()
        # For asynchronous tasks on the thread pool
        self.tag = 'master'
        self.shares = ['threadPool', 'logger']

        self.lock = threading.RLock()
        # Time limit (secs) that GUI should update within or get a warning
        self.update_limit = 1.0

        # Registrations for channels that plugins want to subscribe to
        self.regChannels = {}
        self.model.add_callback('channel-arrived', self.update_channels)

        # Holds plugin registrations for specific status items
        self.regSelect = {}
        self.model.add_callback('status-arrived', self.update_status)

        self.get_status_handle()

        # Holds plugin registrations for configuration changes
        self.register_select('chg-config', self.change_config,
                             ['FITS.SBR.MAINOBCP', 'STATL.TSC_F_SELECT'])


    def get_model(self):
        return self.model

    def stop(self):
        self.ev_quit.set()

    def register_channels(self, ident, cb_fn, channels):
        # channels can be supplied as either a comma-separated string
        # or as a list or a set
        if type(channels) == str:
            channels = set([c.strip() for c in channels.split(',')])
        else:
            channels = set(channels)
        for channel in channels:
            if channel in self.regChannels:
                self.regChannels[channel].append((ident, cb_fn))
            else:
                self.regChannels[channel] = [(ident, cb_fn)]
        self.model.update_channel_list(channels)

    def update_channels(self, model, path, value):
        # This code assumes that the path is of the form
        # '<prefix>.<channel_name>.<rest_of_path>, so we can extract
        # the channel name from the second component in the path.
        pathComponents = path.split('.')
        # Ignore the message if we can't find the channel name or the
        # regChannels data structure has no information on the
        # channel.
        if len(pathComponents) > 1:
            channel = pathComponents[1]
            if channel in self.regChannels:
                for i in range(len(self.regChannels[channel])):
                    (ident, cb_fn) = self.regChannels[channel][i]
                    self.gui_do(self.error_wrap, cb_fn, path, value)

    def get_status_handle(self):
        self.proxystatus = ro.remoteObjectProxy('status')

    def update_status(self, model, statusInfo):
        self.logger.debug("status arrived: %s" % (str(statusInfo)))

        start_time = time.time()
        self.last_update = start_time

        if len(statusInfo) == 0:
            return

        aliasset = set(statusInfo.keys())

        for cbkey in self.regSelect.keys():
            aliases, cb_fn = self.regSelect[cbkey]
            s = aliases.intersection(aliasset)
            if len(s) > 0:
                statusDict = {}.fromkeys(aliases)
                model.fetch(statusDict)

                try:
                    self.logger.debug("updating '%s'" % (cbkey))
                    self.gui_do(self.error_wrap, cb_fn, statusDict)

                except Exception as e:
                    self.logger.error("Error making callback to '%s': %s" % (
                        cbkey, str(e)))
                    # TODO: log traceback

        end_time = time.time()
        elapsed = end_time - start_time
        if elapsed > self.update_limit:
            diff = elapsed -  self.update_limit
            self.logger.warn("Elapsed update time exceeded limit by %.2f sec" % (
                diff))

    def register_select(self, ident, cb_fn, aliases):
        aliases = set(aliases)
        self.regSelect[ident] = (aliases, cb_fn)

        need_aliases = self.model.calc_missing_aliases(aliases)
        self.nongui_do(self.fetch_missing_aliases, aliases)

    def fetch_missing_aliases(self, aliases):
        # Fetch those aliases and update our model
        statusDict = {}.fromkeys(aliases)
        try:
            statusInfo = self.proxystatus.fetch(statusDict)

            self.model.update_statusInfo(statusInfo)

        except Exception as e:
            self.logger.error("Error fetching needed status items: %s" % (
                str(e)))

    def change_config(self, statusDict):

        d = { 'foci': statusDict['STATL.TSC_F_SELECT'],
              'inst': statusDict['FITS.SBR.MAINOBCP'],
              }
        self.make_callback('change-config', d)


    def play_soundfile(self, filepath, format=None, priority=20):
        self.logger.debug("Subclass could override this to play sound file '%s'" % (
            filepath))

    def gui_do(self, method, *args, **kwdargs):
        """General method for asynchronously calling into the GUI.
        It makes a future to call the given (method) with the given (args)
        and (kwdargs) inside the gui thread.  If the calling thread is a
        non-gui thread the future is returned.
        """
        future = Future.Future()
        future.freeze(method, *args, **kwdargs)
        self.gui_queue.put(future)

        my_id = thread.get_ident()
        if my_id != self.gui_thread_id:
            return future

    def gui_call(self, method, *args, **kwdargs):
        my_id = thread.get_ident()
        if my_id == self.gui_thread_id:
            return method(*args, **kwdargs)
        else:
            future = self.gui_do(method, *args, **kwdargs)
            return future.wait()

    def gui_do_future(self, future):
        self.gui_queue.put(future)
        return future

    def nongui_do(self, method, *args, **kwdargs):
        task = Task.FuncTask(method, args, kwdargs, logger=self.logger)
        return self.nongui_do_task(task)

    def nongui_do_cb(self, tup, method, *args, **kwdargs):
        task = Task.FuncTask(method, args, kwdargs, logger=self.logger)
        task.register_callback(tup[0], args=tup[1:])
        return self.nongui_do_task(task)

    def nongui_do_task(self, task):
        try:
            task.init_and_start(self)
            return task
        except Exception as e:
            self.logger.error("Error starting task: %s" % (str(e)))
            raise(e)

    def assert_gui_thread(self):
        my_id = thread.get_ident()
        assert my_id == self.gui_thread_id, \
               ControlError("Non-GUI thread (%d) is executing GUI code!" % (
            my_id))

    def assert_nongui_thread(self):
        my_id = thread.get_ident()
        assert my_id != self.gui_thread_id, \
               ControlError("GUI thread (%d) is executing non-GUI code!" % (
            my_id))

    def error_wrap(self, method, *args, **kwargs):
        try:
            return method(*args, **kwargs)

        except Exception as e:
            errmsg = "\n".join([e.__class__.__name__, str(e)])
            try:
                (type, value, tb) = sys.exc_info()
                tb_str = "\n".join(traceback.format_tb(tb))
            except Exception as e:
                tb_str = "Traceback information unavailable."
                errmsg += tb_str
                self.logger.error(errmsg)

    def mainloop(self, timeout=0.001):
        # Mark our thread id
        self.gui_thread_id = thread.get_ident()

        while not self.ev_quit.isSet():
            self.update_pending(timeout=timeout)

# END
