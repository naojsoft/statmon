#
# alarm_gui.py -- GUI to monitor alarm-related Gen2 status aliases and
#                 display alarms.
#
# Cross-backend (Ginga-wrapped) version: builds itself out of
# Widgets.TableView / TabWidget / Button / Label / ToggleButton, so the
# same plugin runs under qtw, gtk3w, gtk4w, or pgw.
#
# Russell Kackley (rkackley@naoj.org)
# E. Jeschke
#

import os
import time
import threading

from g2base.remoteObjects import Monitor

from Gen2.alarm import StatusValHistory   # noqa: F401  (used by callers)

from ginga.gw import Widgets


# Default persistent data file
default_persist_data_filename = 'alarm_handler3.pickle'

# Per-severity row styling, applied via ``TableView.set_row_color``.
# Coloured-text-on-bold-weight, no background fill — Qt's
# ``setItemWidget`` (used for the per-row Mute checkbox and Reset
# button) suppresses the QTreeWidgetItem background brush, so a
# bg-based scheme would look inconsistent across the row.  Bold
# coloured text is honoured uniformly by every backend.
#
# The keys are *prefixes* — the alarm handler emits values like
# ``CriticalHi`` / ``CriticalLo`` / ``WarningHi`` / ``WarningLo``
# in addition to the bare names, and we want them all to map to
# the same style.  Order matters: longer prefixes first so e.g.
# ``Critical`` is checked before ``Ok`` (no overlap today, but
# leaves room for ``OkHi`` and friends).
_SEVERITY_PREFIXES = (
    ('Critical', '#cc0000', True),   # red, bold
    ('Warning',  '#cc6a00', True),   # amber, bold
    ('Ok',       '#1a7f1a', True),   # green, bold
    ('Info',     '#444444', False),  # dark grey, normal
)


def _severity_style(severity):
    """Map a severity string (possibly with a Hi/Lo suffix) to
    ``(fg, bold)``.  Unknown severities return ``(None, None)``
    so the row gets default styling."""
    if not severity:
        return None, None
    for prefix, fg, bold in _SEVERITY_PREFIXES:
        if severity.startswith(prefix):
            return fg, bold
    return None, None


def _format_alarm_row(timestamp, ID, Name, severity):
    """Format an alarm tuple as a row dict for the TableView.

    The severity *colour* is applied separately via
    ``set_row_color`` after ``set_rows`` so the cell text stays
    clean even on backends that can't honour the colour."""
    timestr = time.strftime('%Y-%b-%d %H:%M:%S',
                            time.localtime(timestamp))
    return {
        'Time': timestr,
        'ID': ID,
        'Name': Name,
        'Severity': severity,
    }


def _format_active_alarm_row(timestamp, ID, Name, severity, muteOn,
                             userCanMute, userCanReset):
    """Active-table row.  Same shape as ``_format_alarm_row`` plus
    the per-row Mute checkbox state, a Reset button placeholder,
    and the two permission flags that drive the per-row widget
    enabled / visible gates declared on the column descriptors."""
    row = _format_alarm_row(timestamp, ID, Name, severity)
    row['muteOn'] = bool(muteOn)
    row['reset'] = None
    row['userCanMute'] = bool(userCanMute)
    row['userCanReset'] = bool(userCanReset)
    return row


class MainWindow:
    """Cross-backend alarm-monitor GUI.

    Build with ``MainWindow(alhProxy, logger, gui_do=...)`` then
    ``build_gui(container)`` to populate the given Ginga container
    (a VBox is typical).

    Worker threads can call ``updateTime`` / ``addAlarm`` /
    ``checkActiveAlarms`` directly — those re-dispatch through the
    supplied ``gui_do`` callable to run actual widget mutations on
    the GUI thread.  When ``gui_do`` is ``None`` (e.g. a standalone
    test) the calls run synchronously in the caller's thread.

    The watchdog timer (``WATCHDOG_SECONDS`` of no time updates →
    insert a "Alarm handler conn. lost" warning row) is wired
    internally via ``threading.Timer``.
    """

    WATCHDOG_SECONDS = 5.0

    def __init__(self, alhProxy, logger, gui_do=None):
        self.alhProxy = alhProxy
        self.logger = logger
        # gui_do dispatches a callable to the GUI thread.  When the
        # caller is already on that thread (e.g. inside a Ginga
        # plugin's build_gui path), this can be the no-op below
        # since ginga.gui_do queues to itself harmlessly anyway.
        self.gui_do = gui_do or self._sync_dispatch

        # Shadow state — the source of truth for what the active /
        # history tables show.  All mutations happen on the GUI
        # thread (via gui_do dispatching) so no locking needed.
        # Each active row: [timestamp, ID, Name, severity, muteOn,
        #                   userCanMute, userCanReset]
        # Each history row: [timestamp, ID, Name, severity]
        self._active_rows = []
        self._history_rows = []

        self._last_time_update = None
        self._watchdog = None
        self._watchdog_lock = threading.Lock()

    # ----- GUI construction -----------------------------------

    def build_gui(self, container):
        """Populate ``container`` (a Ginga VBox-like) with the alarm
        GUI.  Call once, after construction."""
        container.set_margins(4, 4, 4, 4)
        container.set_spacing(4)
        container.set_expanding(True, True)

        # Connection-status / heartbeat label at the top.
        self.time_label = Widgets.Label('No time signal!')
        self.time_label.set_color(fg='red')
        container.add_widget(self.time_label, stretch=0)

        # Tabs for Active vs History.
        self.tabs = Widgets.TabWidget()
        container.add_widget(self.tabs, stretch=1)

        # ----- Active tab --------------------------------------
        active_vbox = Widgets.VBox()
        active_vbox.set_spacing(4)

        self.active_table = Widgets.TableView(
            columns=[
                {'label': 'Time',     'key': 'Time',     'type': 'string',
                 'colwidth': 150},
                {'label': 'ID',       'key': 'ID',       'type': 'string',
                 'colwidth': 10},
                {'label': 'Name',     'key': 'Name',     'type': 'string',
                 'colwidth': 140},
                {'label': 'Severity', 'key': 'Severity', 'type': 'string',
                 'colwidth': 85},
                # Per-row Mute checkbox + Reset button — matches
                # the original Qt version's layout.  Toggling the
                # checkbox fires ``cell_edited``; clicking Reset
                # fires ``cell_action``.  ``enabled_key`` /
                # ``visible_key`` name row-dict fields that gate
                # the per-row widget: the Mute checkbox is greyed
                # out when ``userCanMute`` is False, and the Reset
                # button is suppressed entirely when
                # ``userCanReset`` is False (cell stays empty).
                {'label': 'Mute',     'key': 'muteOn',   'type': 'bool',
                 'widget': 'checkbox', 'colwidth': 10,
                 'enabled_key': 'userCanMute'},
                {'label': '',         'key': 'reset',    'type': 'string',
                 'widget': 'button', 'text': 'Reset', 'colwidth': 20,
                 'visible_key': 'userCanReset'},
            ],
            selection_mode='single',
            show_row_numbers=False,
            show_grid=True,
            #show_grid=False,
            sortable=True,
        )
        self.active_table.add_callback('cell_edited',
                                       self._on_active_cell_edited)
        self.active_table.add_callback('cell_action',
                                       self._on_active_cell_action)
        active_vbox.add_widget(self.active_table, stretch=1)

        self.tabs.add_widget(active_vbox, title='Active')

        # ----- History tab -------------------------------------
        history_vbox = Widgets.VBox()
        self.history_table = Widgets.TableView(
            columns=[
                {'label': 'Time',     'key': 'Time',     'type': 'string'},
                {'label': 'ID',       'key': 'ID',       'type': 'string'},
                {'label': 'Name',     'key': 'Name',     'type': 'string'},
                {'label': 'Severity', 'key': 'Severity', 'type': 'string'},
            ],
            selection_mode='single',
            show_row_numbers=False,
            show_grid=True,
            #show_grid=False,
            sortable=True,
        )
        history_vbox.add_widget(self.history_table, stretch=1)
        self.tabs.add_widget(history_vbox, title='History')

        # Watchdog: if no time update arrives within
        # WATCHDOG_SECONDS, surface an "Alarm handler conn. lost"
        # warning row.  Start it now so a never-connected handler
        # still surfaces the problem.
        self._restart_watchdog()

    def get_widget(self):
        """Return the underlying widget object — kept for backward
        compatibility with callers that used to wrap a QWidget."""
        return self.tabs

    # ----- thread-safe public API -----------------------------

    def updateTime(self, text):
        """Heartbeat from the alarm handler."""
        self.gui_do(self._update_time_label, text)

    def addAlarm(self, timestamp, ID, Name, alarmState, muteOn,
                 userCanMute, userCanReset, acknowledged):
        """Add or update an alarm.  Mirrors the old Qt version's
        signature so the module-level ``initializeAlarmWindow`` /
        ``updateAlarmWindow`` helpers can call it unchanged."""
        # Push to history (excluding the housekeeping "no active
        # alarms" placeholder, matching the old behaviour).
        if ID != 'N/A' or alarmState != 'Info':
            self.gui_do(self._add_history,
                        [timestamp, ID, Name, alarmState])
        # Update the active-alarm list.
        self.gui_do(self._update_active,
                    [timestamp, ID, Name, alarmState, muteOn,
                     userCanMute, userCanReset])

    def checkActiveAlarms(self, timestamp):
        self.gui_do(self._check_active_alarms, timestamp)

    # ----- internal GUI-thread handlers -----------------------

    @staticmethod
    def _sync_dispatch(fn, *args, **kwargs):
        """Default ``gui_do`` when none was supplied — just call
        the function directly.  Suitable for standalone tests."""
        fn(*args, **kwargs)

    def _update_time_label(self, text):
        self._last_time_update = text
        self.time_label.set_text(text)
        self.time_label.set_color(fg='forestgreen')
        # If we'd previously inserted the "conn. lost" row, take it
        # out now that the handler is back.
        self._remove_active(ID='N/A',
                            name='Alarm handler conn. lost',
                            severity='Warning')
        # Reset the heartbeat watchdog.
        self._restart_watchdog()

    def _add_history(self, alarm):
        self._history_rows.append(list(alarm))
        self.history_table.set_rows(
            [_format_alarm_row(*r) for r in self._history_rows])
        self._apply_severity_colors(self.history_table,
                                    self._history_rows)

    def _update_active(self, alarm):
        timestamp, ID, Name, severity, muteOn, userCanMute, userCanReset = alarm
        if severity == 'Ok':
            # ``Ok`` means the alarm has cleared — remove it from
            # the active list (the old version did the same).
            self._remove_active(ID=ID)
            return

        # Update in place if we already have this ID; otherwise
        # append.
        for r in self._active_rows:
            if r[1] == ID:
                r[0] = timestamp
                r[2] = Name
                r[3] = severity
                r[4] = muteOn
                r[5] = userCanMute
                r[6] = userCanReset
                break
        else:
            self._active_rows.append(list(alarm))

        self._refresh_active_table()

    def _remove_active(self, ID=None, name=None, severity=None):
        """Remove the first active-row matching the given filter
        keys (each one independently optional)."""
        for i, r in enumerate(self._active_rows):
            if ID is not None and r[1] != ID:
                continue
            if name is not None and r[2] != name:
                continue
            if severity is not None and r[3] != severity:
                continue
            del self._active_rows[i]
            self._refresh_active_table()
            return

    def _check_active_alarms(self, timestamp):
        """Maintain a single "No Active Alarms" placeholder when
        the active list would otherwise be empty.  Matches the
        old Qt version's behaviour."""
        non_placeholder = [
            r for r in self._active_rows
            if not (r[1] == 'N/A' and r[2] == 'No Active Alarms')
        ]
        has_placeholder = any(
            r[1] == 'N/A' and r[2] == 'No Active Alarms'
            for r in self._active_rows
        )
        if not non_placeholder:
            if not has_placeholder:
                self._active_rows.append(
                    [timestamp, 'N/A', 'No Active Alarms',
                     'Info', True, False, False])
                self._refresh_active_table()
        else:
            if has_placeholder:
                self._remove_active(ID='N/A',
                                    name='No Active Alarms')

    def _refresh_active_table(self):
        self.active_table.set_rows(
            [_format_active_alarm_row(*r) for r in self._active_rows])
        self._apply_severity_colors(self.active_table,
                                    self._active_rows)

    @staticmethod
    def _apply_severity_colors(table, rows):
        """Paint each visible row in ``table`` according to its
        severity (rows[i][3]) — coloured bold text via
        ``_severity_style`` (which prefix-matches so CriticalHi,
        WarningLo, etc. map to the bare-severity style).  No
        background fill (see the module-level comment for why)."""
        for i, r in enumerate(rows):
            fg, bold = _severity_style(r[3])
            if fg is not None or bold is not None:
                table.set_row_color([i], fg=fg, bold=bold)

    # ----- per-row Mute / Reset callbacks ---------------------

    def _on_active_cell_edited(self, table, path, col_key, old, new):
        """Fired when the per-row Mute checkbox toggles.  Resolve
        the row via the table (so sort order is respected), look
        the alarm up by ID in the shadow state, and forward to
        the proxy."""
        if col_key != 'muteOn' or not path:
            return
        try:
            row = table.get_row(path[0])
        except Exception:
            return
        ID = row.get('ID')
        severity = row.get('Severity')
        # Skip the housekeeping placeholders ("No Active Alarms",
        # "Alarm handler conn. lost") — they use ID='N/A'.
        if not ID or ID == 'N/A':
            return
        try:
            if new:
                self.alhProxy.muteOn(ID, severity)
            else:
                self.alhProxy.muteOff(ID, severity)
        except Exception as e:
            self.logger.error(
                f"mute toggle for {ID}/{severity} failed: {e}")
            return
        # Reflect the new state in the shadow rows so a full
        # refresh keeps the checkbox in sync.
        for r in self._active_rows:
            if r[1] == ID:
                r[4] = bool(new)
                break

    def _on_active_cell_action(self, table, row_dict, col_key):
        """Fired when the per-row Reset button is clicked."""
        if col_key != 'reset' or not row_dict:
            return
        ID = row_dict.get('ID')
        severity = row_dict.get('Severity')
        if not ID or ID == 'N/A':
            return
        self.logger.info(
            f"reset clicked: ID={ID} severity={severity}")
        try:
            r = self.alhProxy.resetAlarm(ID, severity)
            self.logger.info(f"resetAlarm returned {r!r}")
        except Exception as e:
            self.logger.error(
                f"resetAlarm for {ID}/{severity} failed: {e}")

    # ----- watchdog -------------------------------------------

    def _restart_watchdog(self):
        with self._watchdog_lock:
            if self._watchdog is not None:
                self._watchdog.cancel()
            self._watchdog = threading.Timer(
                self.WATCHDOG_SECONDS, self._on_watchdog_expire)
            self._watchdog.daemon = True
            self._watchdog.start()

    def _on_watchdog_expire(self):
        # Runs on the timer thread — dispatch back to the GUI
        # thread before touching widgets.
        self.gui_do(self._on_watchdog_expire_gui)

    def _on_watchdog_expire_gui(self):
        if self._last_time_update:
            self.time_label.set_text(self._last_time_update)
            self.time_label.set_color(fg='red')
        self.addAlarm(time.time(), 'N/A',
                      'Alarm handler conn. lost', 'Warning',
                      False, True, False, True)
        # Re-arm so we keep flagging the loss every
        # WATCHDOG_SECONDS until the handler comes back.
        self._restart_watchdog()


# =============================================================
# Module-level helpers — same names / signatures as before so
# the Alarm.py plugin doesn't need to change much.
# =============================================================

def initializeAlarmWindow(mainWindow, svConfig, statusValHistory,
                          statusFromGen2):
    """Populate the alarm window from the saved status-value
    history file *and* from the current Gen2 alarm channel.

    This is the verbatim logic from the original Qt-based version
    — only the GUI side downstream changed.
    """
    # ---- History → mainWindow ---------------------------------
    history = {}
    for ID in statusValHistory.history:
        historyID = statusValHistory.history[ID]
        if len(historyID) > 1:
            i = 0
            for statusVal in historyID:
                timestamp = statusVal.timestamp
                if i == 0:
                    if statusVal.alarmState != 'Ok':
                        history.setdefault(timestamp, {})[ID] = statusVal
                else:
                    if statusVal.alarmState != 'Ok' or \
                       (statusVal.alarmState == 'Ok'
                        and historyID[i - 1].alarmState != 'Ok'):
                        history.setdefault(statusVal.timestamp, {})[ID] \
                            = statusVal
                i += 1
        else:
            statusVal = historyID[0]
            if statusVal.alarmState != 'Ok':
                history.setdefault(statusVal.timestamp, {})[ID] = statusVal

    for timestamp in sorted(history):
        for ID in history[timestamp]:
            historyItem = history[timestamp][ID]
            alarmItem = {
                'Name': None, 'timestamp': timestamp,
                'value': historyItem.value,
                'alarmState': historyItem.alarmState,
                'varType': None, 'units': None,
                'audioFilename': None,
                'muteOn': historyItem.muteOn,
                'userCanMute': None, 'userCanReset': None,
                'visible': None, 'acknowledged': False,
            }
            if ID in svConfig.configID:
                alarmItem['visible'] = svConfig.getVisibleState(
                    historyItem.alarmState, ID)
                if alarmItem['visible']:
                    svConfigItem = svConfig.configID[ID]
                    alarmItem['Name'] = svConfigItem.Name
                    alarmItem['varType'] = svConfigItem.Type
                    if alarmItem['varType'] == 'Analog':
                        alarmItem['units'] = svConfigItem.Units
                    if historyItem.alarmState in svConfigItem.Alarm:
                        alarmItem['audioFilename'] = \
                            svConfigItem.Alarm[historyItem.alarmState].Audio
                    mainWindow.addAlarm(
                        alarmItem['timestamp'], ID,
                        alarmItem['Name'], alarmItem['alarmState'],
                        alarmItem['muteOn'], alarmItem['userCanMute'],
                        alarmItem['userCanReset'],
                        alarmItem['acknowledged'])

    # ---- Current Gen2 status → mainWindow ---------------------
    for ID in svConfig.configID:
        alias = 'ALARM_' + ID
        if alias in statusFromGen2:
            if isinstance(statusFromGen2[alias], dict):
                alarmItem = statusFromGen2[alias]
                if alarmItem['alarmState'] != 'Ok':
                    mainWindow.addAlarm(
                        alarmItem['timestamp'], ID,
                        alarmItem['Name'], alarmItem['alarmState'],
                        alarmItem['muteOn'], alarmItem['userCanMute'],
                        alarmItem['userCanReset'],
                        alarmItem['acknowledged'])

    mainWindow.checkActiveAlarms(time.time())


def updateAlarmWindow(mainWindow, svConfig, statusFromGen2):
    """Push a (partial) Gen2 status update into the alarm window."""
    for ID in svConfig.configID:
        alias = 'ALARM_' + ID
        if alias in statusFromGen2:
            if isinstance(statusFromGen2[alias], dict):
                alarmItem = statusFromGen2[alias]
                mainWindow.addAlarm(
                    alarmItem['timestamp'], ID,
                    alarmItem['Name'], alarmItem['alarmState'],
                    alarmItem['muteOn'], alarmItem['userCanMute'],
                    alarmItem['userCanReset'],
                    alarmItem['acknowledged'])

    # Heartbeat path: the alarm handler periodically sends an
    # AlarmHandlerPing record so we can detect when it's gone away.
    alarm_dict = statusFromGen2.get('ALARM_AlarmHandlerPing', None)
    if alarm_dict is not None:
        timeStr = time.asctime(time.localtime(alarm_dict['timestamp']))
        mainWindow.updateTime(timeStr)

    mainWindow.checkActiveAlarms(time.time())


def mon_alarm_cb(payload, logger, lock, mainWindow, svConfig):
    """Monitor callback for payloads on the 'alarm' channel."""
    try:
        bnch = Monitor.unpack_payload(payload)
        if not bnch.path.startswith('mon.alarm.alarm_handler'):
            return

        logger.info(f"bnch.value {bnch.value}")
        with lock:
            aliasName = 'ALARM_' + bnch.value['ID']
            statusDict = {aliasName: bnch.value}
            if mainWindow:
                updateAlarmWindow(mainWindow, svConfig, statusDict)

    except Monitor.MonitorError as e:
        logger.error(f"monitor error: {e}")

    except Exception as e:
        logger.error(f"Exception in alarm_cb: {e}", exc_info=True)
