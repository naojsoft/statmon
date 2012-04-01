import time
import threading

import remoteObjects.Monitor as Monitor
import Callback

# import from SOSS.status ?
statNone = '##STATNONE##'

class StatusModel(Callback.Callbacks):

    def __init__(self, logger):
        super(StatusModel, self).__init__()
        
        self.logger = logger

        self.lock = threading.RLock()
        # This is where we store all incoming status
        self.statusDict = {}
        
        # Enable callbacks that can be registered
        for name in ('status-all', 'status-select'):
            self.enable_callback(name)

        self.regSelect = {}
        
    def arr_status(self, payload, name, channels):
        """Called when new status information arrives at the periodic
        interval.
        """
        #self.logger.debug("received values '%s'" % str(payload))
        try:
            bnch = Monitor.unpack_payload(payload)

        except Monitor.MonitorError:
            self.logger.error("malformed packet '%s': %s" % (
                str(payload), str(e)))
            return

        if bnch.path != 'mon.status':
            return
        
        statusInfo = bnch.value
        with self.lock:
            self.statusDict.update(statusInfo)

        self.update_status(statusInfo)


    def update_status(self, statusInfo):
        self.logger.debug("status arrived: %s" % (str(statusInfo)))

        if len(statusInfo) == 0:
            return

        start_time = time.time()

        aliasset = set(statusInfo.keys())

        for cbkey in self.regSelect.keys():
            aliases, cb_fn = self.regSelect[cbkey]
            s = aliases.intersection(aliasset)
            if len(s) > 0:
                # python 3.X
                #statusDict = { alias: self.statusDict[alias] for alias in aliases }
                statusDict = {}
                for alias in aliases:
                    statusDict[alias] = self.statusDict.get(alias,
                                                            statNone)
                
                # TODO: can we use make_callback for this?
                try:
                    cb_fn(statusDict)
                except Exception, e:
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
        self.regSelect[ident] = (set(aliases), cb_fn)
            
        
# END

