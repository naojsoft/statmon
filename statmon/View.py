#
# Viewer.py -- Qt display handler for StatMon.
#
# E. Jeschke
#
# stdlib imports
import sys, os
import queue as Queue
import traceback

# GUI imports
from ginga.gw import Widgets, Desktop, GwMain
from qtpy import QtWidgets, QtCore, QtGui
from ginga.misc import Bunch

moduleHome = os.path.split(sys.modules[__name__].__file__)[0]
icon_path = os.path.abspath(os.path.join(moduleHome, '..', 'icons'))
rc_file = os.path.join(moduleHome, "qt_rc")


class ViewError(Exception):
    """Exception raised for errors in this module."""
    pass

class Viewer(GwMain.GwMain, Widgets.Application):

    def __init__(self, logger, ev_quit):
        # Create the top level Qt app
        Widgets.Application.__init__(self, logger=logger)
        GwMain.GwMain.__init__(self, logger=logger, ev_quit=ev_quit, app=self)

        # QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        # QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())

        # read in any module-level style sheet
        if os.path.exists(rc_file):
            self.app.setStyleSheet(rc_file)

        # defaults for height and width
        self.default_height = min(900, self.screen_ht - 100)
        self.default_width  = min(1600, self.screen_wd)

        # This is where all the widgets get stored
        self.w = Bunch.Bunch()
        self.iconpath = icon_path

        # Default fonts for our all
        self.font = Bunch.Bunch(mono12=QtGui.QFont('Monospace', 12),
                                mono11=QtGui.QFont('Monospace', 11))

        QtWidgets.QToolTip.setFont(self.font.mono11)

        # For now...
        self.controller = self

        # dictionary of plugins
        self.plugins = {}

        #self.add_callback('close', self.close_cb)
        self.add_callback('shutdown', self.shutdown_cb)

    def build_toplevel(self, layout):
        # Dynamically create the desktop layout
        self.ds = Desktop.Desktop(self)
        self.ds.make_desktop(layout, widget_dict=self.w)
        #self.ds.add_callback('all-closed', self.quit)

        root = self.ds.toplevels[0]
        self.w.root = root
        # TEMP: temporarily needed until "all-closed" callback from Desktop is working
        #root.add_callback('close', self.quit)
        root.add_callback('close', self.close_cb)

        # Add menubar and menus, if desired
        self.add_menus()

        # Add popup dialogs
        self.add_dialogs()

        # Add status bar, if desired
        self.add_statusbar()

        return root


    def add_menus(self):
        """Subclass should override this to create a custom menu bar
        or to omit a menu bar.
        """
        pass

    def add_dialogs(self):
        """Subclass should override this to create their own necessary
        dialogs.
        """
        pass

    def add_statusbar(self):
        """Subclass should override this to create their own status bar
        or to omit a status bar.
        """
        pass

    def set_titlebar(self, text):
        """Sets the title of the top level window.
        """
        self.w.root.set_title(text)

    def load_plugin(self, pluginName, moduleName, className, wsName, tabName):

        widget = Widgets.VBox()

        # Record plugin info
        canonicalName = pluginName.lower()
        bnch = Bunch.Bunch(caseless=True,
                           name=canonicalName, officialname=pluginName,
                           modulename=moduleName, classname=className,
                           wsname=wsName, tabname=tabName, widget=widget)

        self.plugins[pluginName] = bnch

        try:
            module = self.mm.load_module(moduleName)

            # Look up the module and class
            module = self.mm.get_module(moduleName)
            klass = getattr(module, className)

            # instantiate the class
            pluginObj = klass(self.model, self, self.controller,
                              self.logger)

            # Save a reference to the plugin object so we can use it
            # later
            self.plugins[pluginName].setvals(obj=pluginObj)

            # Build the plugin GUI
            pluginObj.build_gui(widget)

            # Add the widget to a workspace and save the tab name in
            # case we need to delete the widget later on.
            dsTabBnch = self.ds.add_tab(wsName, widget, 2, tabName)
            dsTabName = dsTabBnch.tabname
            self.plugins[pluginName].setvals(wsTabName=dsTabName)

            # Start the plugin
            pluginObj.start()

        except Exception as e:
            errstr = "Plugin '%s' failed to initialize: %s" % (
                className, str(e))
            self.logger.error(errstr)
            try:
                (type, value, tb) = sys.exc_info()
                tb_str = "\n".join(traceback.format_tb(tb))
                self.logger.error("Traceback:\n%s" % (tb_str))

            except Exception as e:
                tb_str = "Traceback information unavailable."
                self.logger.error(tb_str)

            textw = Widgets.TextArea(editable=False, wrap=True)
            textw.set_text(str(e) + '\n')
            textw.append_text(tb_str)
            widget.add_widget(textw, stretch=1)

            self.ds.add_tab(wsName, widget, 2, tabName)

    def close_plugin(self, pluginName):
        bnch = self.plugins[pluginName]
        self.logger.info('calling stop() for plugin %s' % (pluginName))
        bnch.obj.stop()
        self.logger.info('calling remove_tab() for plugin %s' % (pluginName))
        self.ds.remove_tab(bnch.wsTabName)
        return True

    def close_all_plugins(self):
        for pluginName in self.plugins:
            try:
                self.close_plugin(pluginName)
            except Exception as e:
                self.logger.error('Exception while calling stop for plugin %s: %s' % (pluginName, e))
        return True

    def reload_plugin(self, pluginName):
        pInfo = self.plugins[pluginName]
        try:
            self.close_plugin(pluginName)
        except:
            pass

        return self.load_plugin(pInfo.officialname, pInfo.modulename,
                                pInfo.classname, pInfo.wsname,
                                pInfo.tabname)

    def statusMsg(self, msg, duration=None, iserror=False):
        """Send a message to the status bar.  If (duration) is specified
        then the message will disappear after that many seconds.
        """
        # TODO: turn background of bar red for duration if iserror==True
        if duration:
            self.w.status.set_message(msg, duration=duration)
        else:
            self.w.status.set_message(msg)

    def error(self, text, duration=None):
        """Convenience function to log an error to the error log and also
        display it in the status bar as an error.
        """
        self.logger.error(text)
        self.statusMsg(text, duration=duration, iserror=True)

    def setPos(self, x, y):
        """Set the position of the root window."""
        self.w.root.move(x, y)

    def setSize(self, w, h):
        """Set the size of the root window."""
        self.w.root.resize(w, h)

    def set_geometry(self, geometry):
        """Set the geometry of the root window.  (geometry) is expected to
        be an X-style geometry string; e.g. 1000x900+100+200
        """
        # Painful translation of X window geometry specification
        # into correct calls to Qt
        coords = geometry.replace('+', ' +')
        coords = coords.replace('-', ' -')
        coords = coords.split()
        if 'x' in coords[0]:
            # spec includes dimensions
            dim = coords[0]
            coords = coords[1:]
        else:
            # spec is position only
            dim = None

        if dim != None:
            # user specified dimensions
            dim = map(int, dim.split('x'))
            self.setSize(*dim)

        if len(coords) > 0:
            # user specified position
            coords = map(int, coords)
            self.setPos(*coords)


    ####################################################
    # CALLBACKS
    ####################################################

    def close_cb(self, app):
        # confirm close with a dialog here
        q_quit = Widgets.MessageDialog(title="Confirm Quit", modal=False,
                                       parent=self.w.root,
                                       buttons=[("Cancel", False),
                                                ("Confirm", True)])
        # necessary so it doesn't get garbage collected right away
        self.w.quit_dialog = q_quit
        q_quit.set_message('question', "Do you really want to quit?")
        q_quit.add_callback('activated', self._confirm_quit_cb)
        q_quit.add_callback('close', lambda w: self._confirm_quit_cb(w, False))
        q_quit.show()

    def _confirm_quit_cb(self, w, tf):
        self.w.quit_dialog.delete()
        self.w.quit_dialog = None
        if not tf:
            return

        self.quit()

    def shutdown_cb(self, app):
        """Quit the application.
        """
        self.quit()

    def quit(self, *args):
        """Quit the application.
        """
        self.logger.info("closing all plugins...")
        self.close_all_plugins()

        self.logger.info("Attempting to shut down the application...")
        self.stop()
