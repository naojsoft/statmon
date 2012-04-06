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
        for name in ['status-arrived', ]:
            self.enable_callback(name)

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

        self.make_callback('status-arrived', statusInfo)

    def fetch(self, fetchDict):
        with self.lock:
            for key in fetchDict.keys():
                fetchDict[key] = self.statusDict.get(key, statNone)
                
# END

