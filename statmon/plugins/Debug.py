#
# Debug.py -- Debugging plugin for StatMon
#
# E. Jeschke
#
import PlBase

from ginga.gw import Widgets

class Debug(PlBase.Plugin):

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(4, 4, 4, 4)
        self.root.set_spacing(2)

        self.msgFont = "Fixed"
        tw = Widgets.TextArea(editable=False)
        tw.set_font(self.msgFont, size=14)
        self.tw = tw
        self.history = []
        self.histmax = 10

        self.root.add_widget(tw, stretch=1)

        self.entry = Widgets.TextEntry()
        self.root.add_widget(self.entry, stretch=0)
        self.entry.add_callback('activated', lambda w: self.command_cb(self.entry))

    def start(self):
        pass

    def closePlugin(self, plname):
        self.view.close_plugin(plname)
        return True

    def reloadPlugin(self, plname):
        #self.view.close_plugin(plname)
        self.view.reload_plugin(plname)
        return True

    def reloadModule(self, name):
        self.controller.mm.load_module(name)
        return True

    def command(self, cmdstr):
        self.logger.debug("Command is '%s'" % (cmdstr))
        # Evaluate command
        try:
            result = eval(cmdstr)

        except Exception as e:
            result = str(e)
            # TODO: add traceback

        # Append command to history
        self.history.append('>>> ' + cmdstr + '\n' + str(result))

        # Remove all history past history size
        self.history = self.history[-self.histmax:]
        # Update text widget
        self.tw.set_text('\n'.join(self.history))

    def command_cb(self, w):
        # TODO: implement a readline/history type function
        cmdstr = str(w.get_text()).strip()
        self.command(cmdstr)
        w.set_text("")

    def __str__(self):
        return 'debug'

#END
