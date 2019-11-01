#
# Model.py -- Model for StatMon.
#
# Eric Jeschke (eric@naoj.org)
#
import time
import threading

from g2base.remoteObjects import Monitor
from ginga.misc import Callback

# import from SOSS.status ?
statNone = '##STATNONE##'

class StatusModel(Callback.Callbacks):

    def __init__(self, logger):
        super(StatusModel, self).__init__()
        
        self.logger = logger

        self.lock = threading.RLock()
        # This is where we store all incoming status
        self.statusDict = {}

        # Set of channels that we will subscribe to
        self.channels = set()

        # Enable callbacks that can be registered
        for name in ['status-arrived', 'channel-arrived']:
            self.enable_callback(name)

    def store(self, statusInfo):
        with self.lock:
            self.statusDict.update(statusInfo)

    def update_statusInfo(self, statusInfo):
        self.store(statusInfo)
        self.make_callback('status-arrived', statusInfo)

    def fetch(self, fetchDict):
        with self.lock:
            for key in fetchDict.keys():
                fetchDict[key] = self.statusDict.get(key, statNone)
                
    def calc_missing_aliases(self, aliasset):
        with self.lock:
            aliases = self.statusDict.keys()

        # Figure out the set of aliases we don't yet have
        need_aliases = aliasset.difference(set(aliases))
        return need_aliases

    def update_channel_list(self, channels):
        self.channels |= channels

    def arr_channel(self, payload, name, channels):
        """ Called when new information arrives on a channel """
        #self.logger.debug("received values '%s'" % str(payload))
        try:
            bnch = Monitor.unpack_payload(payload)

        except Monitor.MonitorError:
            self.logger.error("malformed packet '%s': %s" % (
                str(payload), str(e)))
            return

        if bnch.path == 'mon.status':
            # status channel gets special treatment
            statusInfo = bnch.value

            self.update_statusInfo(statusInfo)
        else:
            self.make_callback('channel-arrived', bnch.path, bnch.value)
# END

