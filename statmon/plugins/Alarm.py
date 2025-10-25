#
# Alarm.py -- Alarm plugin for statmon
#
# Uses the MainWindow class from alarm_gui.py to create an Alarm GUI
# that can be "plugged in" to statmon.
#
# Russell Kackley (rkackley@naoj.org)
# E. Jeschke
#

import sys
import os
import threading
from ginga.gw import Widgets

from g2base.remoteObjects import remoteObjects as ro

import Gen2.alarm.alarm_gui as AlarmGui
import Gen2.alarm.StatusVar as StatusVar
import Gen2.alarm.StatusValHistory as StatusValHistory
import SOSS.status.common as common
import PlBase

class Alarm(PlBase.Plugin):

    def build_gui(self, container):
        self.firstTime = True
        self.root = container
        self.root.set_margins(4, 4, 4, 4)
        self.root.set_spacing(4)
        self.aliases = []
        self.previousStatusDict = None

        # Set up a connection to the alarm_handler so that the GUI can
        # send messages to it
        self.alhProxy = ro.remoteObjectProxy('alarm_handler')

        # Create the GUI from the MainWindow class in alarm_gui.py
        self.mw = AlarmGui.MainWindow('', self.alhProxy, self.logger,
                                      self.root.get_widget())
        self.root.add_widget(Widgets.wrap(self.mw), stretch=1)

    def start(self):
        self.lock = threading.RLock()
        persistDatafileLock = threading.RLock()

        # Tell alarm_handler process to save its status value history so
        # that we can get the up-date status values from the persistent
        # data file.
        alhProxy = ro.remoteObjectProxy('alarm_handler')
        try:
            alhProxy.saveHistory()
        except ro.remoteObjectError as e:
            self.logger.warn('Warning: unable to connect to alarm_handler to save history: %s' % str(e))

        # The configuration files tell us which Gen2 aliases we want
        # to monitor. The configuration files should be have been
        # installed in the "cfg" module's directory tree.
        cfg_filename = '*_alarm_cfg.yml'
        try:
            import cfg
            cfgDir = os.path.join(os.path.dirname(sys.modules['cfg'].__file__), 'alarm')
        except Exception as e:
            self.logger.error(f'Unable to load cfg module so cannot read configuration file {cfg_filename}')
            raise e
        alarm_cfg_file = os.path.join(cfgDir, cfg_filename)
        self.logger.info(f'alarm_cfg_file is {alarm_cfg_file}')

        # StatusVarConfig reads in the configuration files
        try:
            self.svConfig = StatusVar.StatusVarConfig(alarm_cfg_file, persistDatafileLock, self.logger)
        except Exception as e:
            self.logger.error('Error opening configuration file(s): %s' % str(e))

        statusDict = {}
        try:
            alarmChannelState = self.alhProxy.getMonitorAlarmTree()
            self.logger.info('initial alarm channel %s' % alarmChannelState)
            for ID, value in alarmChannelState.items():
                statusDict['ALARM_' + ID] = value
                self.logger.info('statusDict is {}'.format(statusDict))
        except ro.remoteObjectError as e:
            self.logger.warning('alarm_handler is not running: {}'.format(str(e)))

        # Create a list of all the Gen2 aliases we want to monitor
        self.aliases = []
        #self.aliases.append('STS.TIME1')

        # Default persistent data file
        default_persist_data_filename = AlarmGui.default_persist_data_filename
        try:
            pyhome = os.environ['GEN2COMMON']
            persist_data_dir = os.path.join(pyhome, 'db')
        except:
            persist_data_dir =  os.path.join('/gen2/share/db')

        # If we don't have write access to the persist_data_dir
        # location, use our home directory instead.
        if not os.access(persist_data_dir, os.W_OK):
            persist_data_dir = os.environ['HOME']

        default_persist_data_file = os.path.join(persist_data_dir, default_persist_data_filename)

        # Load the status value history
        self.statusValHistory = StatusValHistory.StatusValHistory(persistDatafileLock, self.logger)
        self.statusValHistory.loadHistory(default_persist_data_file, self.svConfig)

        self.logger.info('Alarm.start calling AlarmGui.initializeAlarmWindow')
        AlarmGui.initializeAlarmWindow(self.mw, self.svConfig, self.statusValHistory, statusDict)

        # Register the update callback function and tell the
        # controller the names of the Gen2 aliases we want to monitor.
        # self.controller.register_select('alarm', self.update, self.aliases)

        self.controller.register_channels('alarm', self.update_channel, 'alarm')

    # changedStatus copies from statusDict only the status values that
    # have changed since the last time we got the update.
    def changedStatus(self, statusDict):
        changedStatusDict = {}
        # Iterate through all the Gen2 status aliases that we are
        # monitoring
        for name in self.aliases:
            # If this status alias is an "ALARM" alias, look at its
            # contents to see if anything has changed since the last
            # time we got the update. If so, add the alarm to the list
            # of changed status values.
            if 'ALARM_' in name:
                currentAlarmItem = statusDict[name]
                try:
                    previousAlarmItem = self.previousStatusDict[name]
                except (TypeError, KeyError) as e:
                    previousAlarmItem = common.STATNONE
                # We cannot check the attributes for changes if either
                # of the currentAlarmItem or previousAlarmItem values
                # are STATERROR or STATNONE
                notAllowed = (common.STATERROR, common.STATNONE)
                if previousAlarmItem not in notAllowed and \
                       currentAlarmItem not in notAllowed:
                    # changed = False
                    # for attribute in currentAlarmItem:
                    #     if currentAlarmItem[attribute] != previousAlarmItem[attribute]:
                    #         changed = True
                    #         break
                    # if changed:
                    #     changedStatusDict[name] = currentAlarmItem
                    if currentAlarmItem != previousAlarmItem:
                        changedStatusDict[name] = currentAlarmItem
                elif previousAlarmItem in notAllowed and \
                         currentAlarmItem not in notAllowed:
                    changedStatusDict[name] = currentAlarmItem
            # elif name == 'STS.TIME1':
            #     # STS.TIME1 is a scalar quantity, so just check to see
            #     # if it has been updated. If so, add it to the list of
            #     # changed status values.
            #     try:
            #         previousValue = self.previousStatusDict[name]
            #     except (TypeError, KeyError)	as e:
            #         previousValue = common.STATNONE
            #     if statusDict[name] != previousValue:
            #         changedStatusDict[name] = statusDict[name]

        # Return the list of changed values
        return changedStatusDict

    # def update(self, statusDict):
    #     with self.lock:
    #         try:
    #             changedStatusDict = self.changedStatus(statusDict)
    #         except TypeError as e:
    #             self.logger.error('Exception %s' % e)
    #             self.logger.debug('previousStatusDict %s' % self.previousStatusDict)
    #             self.logger.debug('current statusDict %s' % statusDict)
    #             changedStatusDict = {}
    #         self.logger.debug(changedStatusDict)
    #         AlarmGui.updateAlarmWindow(self.mw, self.svConfig, changedStatusDict)

    #     # Save the current statusDict information so that we can
    #     # determine if there are any changes the next time around.
    #     self.previousStatusDict = statusDict

    def update_channel(self, path, value):
        if not path.startswith('mon.alarm'):
            return

        with self.lock:
            self.logger.info('path is {} value is {}'.format(path, value))
            changedStatusDict = {'ALARM_' + value['ID']: value}
            AlarmGui.updateAlarmWindow(self.mw, self.svConfig, changedStatusDict)

    def __str__(self):
        return 'alarm'
