#
# Alarm.py -- Alarm plugin for statmon
#
# Uses the MainWindow class from alarm_gui.py to create an Alarm GUI
# that can be "plugged in" to statmon.
#
# R. Kackley
# E. Jeschke
#

import sys
import os
import threading

from g2base.remoteObjects import remoteObjects as ro

import Gen2.alarm.StatusVar as StatusVar
import Gen2.alarm.StatusValHistory as StatusValHistory
import SOSS.status.common as common

import alarm_gui as AlarmGui
import PlBase


class Alarm(PlBase.Plugin):

    def build_gui(self, container):
        self.firstTime = True
        self.aliases = []
        self.previousStatusDict = None

        # Set up a connection to the alarm_handler so that the GUI
        # can send messages to it (muteOn/Off, resetAlarm).
        self.alhProxy = ro.remoteObjectProxy('alarm_handler')

        # Cross-backend Ginga GUI.  ``gui_do`` lets the alarm-gui
        # marshal worker-thread updates onto the GUI thread.
        self.mw = AlarmGui.MainWindow(
            self.alhProxy, self.logger,
            gui_do=self.view.gui_do,
        )
        self.mw.build_gui(container)

    def start(self):
        self.lock = threading.RLock()
        persistDatafileLock = threading.RLock()

        # Tell alarm_handler process to save its status value history
        # so that we can get up-to-date values from the persistent
        # data file.
        alhProxy = ro.remoteObjectProxy('alarm_handler')
        try:
            alhProxy.saveHistory()
        except ro.remoteObjectError as e:
            self.logger.warn(
                f"unable to connect to alarm_handler to save history: {e}")

        # The configuration files tell us which Gen2 aliases we want
        # to monitor.  The configuration files should have been
        # installed in the "cfg" module's directory tree.
        cfg_filename = '*_alarm_cfg.yml'
        try:
            import cfg
            cfgDir = os.path.join(
                os.path.dirname(sys.modules['cfg'].__file__), 'alarm')
        except Exception as e:
            self.logger.error(
                f"Unable to load cfg module so cannot read "
                f"configuration file {cfg_filename}")
            raise e
        alarm_cfg_file = os.path.join(cfgDir, cfg_filename)
        self.logger.info(f"alarm_cfg_file is {alarm_cfg_file}")

        # StatusVarConfig reads in the configuration files.
        try:
            self.svConfig = StatusVar.StatusVarConfig(
                alarm_cfg_file, persistDatafileLock, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error opening configuration file(s): {e}")

        statusDict = {}
        try:
            alarmChannelState = self.alhProxy.getMonitorAlarmTree()
            self.logger.debug(
                f"initial alarm channel {alarmChannelState}")
            for ID, value in alarmChannelState.items():
                statusDict['ALARM_' + ID] = value
                self.logger.debug(f"statusDict is {statusDict}")
        except ro.remoteObjectError as e:
            self.logger.warning(f"alarm_handler is not running: {e}")

        # Reset the list of Gen2 aliases we want to monitor.  (The
        # commented-out STS.TIME1 below was a relic of an earlier
        # heartbeat path; the AlarmHandlerPing channel now serves
        # that purpose.)
        self.aliases = []

        # Default persistent data file.
        default_persist_data_filename = AlarmGui.default_persist_data_filename
        try:
            pyhome = os.environ['GEN2COMMON']
            persist_data_dir = os.path.join(pyhome, 'db')
        except KeyError:
            persist_data_dir = os.path.join('/gen2/share/db')

        # Fall back to $HOME if we can't write the default dir.
        if not os.access(persist_data_dir, os.W_OK):
            persist_data_dir = os.environ['HOME']

        default_persist_data_file = os.path.join(
            persist_data_dir, default_persist_data_filename)

        # Load the status value history.
        self.statusValHistory = StatusValHistory.StatusValHistory(
            persistDatafileLock, self.logger)
        self.statusValHistory.loadHistory(
            default_persist_data_file, self.svConfig)

        self.logger.info(
            'Alarm.start calling AlarmGui.initializeAlarmWindow')
        AlarmGui.initializeAlarmWindow(
            self.mw, self.svConfig, self.statusValHistory, statusDict)

        # Register the channel-update callback.
        self.controller.register_channels(
            'alarm', self.update_channel, 'alarm')

    # changedStatus copies from statusDict only the status values that
    # have changed since the last time we got the update.
    def changedStatus(self, statusDict):
        changedStatusDict = {}
        for name in self.aliases:
            if 'ALARM_' in name:
                currentAlarmItem = statusDict[name]
                try:
                    previousAlarmItem = self.previousStatusDict[name]
                except (TypeError, KeyError):
                    previousAlarmItem = common.STATNONE
                notAllowed = (common.STATERROR, common.STATNONE)
                if previousAlarmItem not in notAllowed and \
                        currentAlarmItem not in notAllowed:
                    if currentAlarmItem != previousAlarmItem:
                        changedStatusDict[name] = currentAlarmItem
                elif previousAlarmItem in notAllowed and \
                        currentAlarmItem not in notAllowed:
                    changedStatusDict[name] = currentAlarmItem

        return changedStatusDict

    def update_channel(self, path, value):
        if not path.startswith('mon.alarm'):
            return

        with self.lock:
            self.logger.debug(f"path is {path} value is {value}")
            changedStatusDict = {'ALARM_' + value['ID']: value}
            # ``updateAlarmWindow`` calls ``mw.addAlarm`` /
            # ``mw.checkActiveAlarms`` / ``mw.updateTime`` which
            # in turn route through ``self.view.gui_do`` before
            # touching any widgets — so this is safe to call
            # straight from the channel thread.
            AlarmGui.updateAlarmWindow(
                self.mw, self.svConfig, changedStatusDict)

    def __str__(self):
        return 'alarm'
