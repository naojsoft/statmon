#
# PlBase.py -- Base class for StatMon plugins
#
# E. Jeschke
#
"""
This class implements the base class for StatMon plugins.  You can add any
convenience methods or classes that would be generally useful across
different plugins.
"""

# instrument on prime/cs/ns focus
pf_inst = ['SPCAM', 'HSC', 'FMOS', 'PFS']
cs_inst = ['MOIRCS', 'FOCAS', 'COMICS', 'SWIMS', 'MIMIZUKU', 'SUKA']
ns_inst = ['IRCS', 'HDS', 'HICIAO', 'K3D', 'CHARIS', 'IRD',
           'VAMPIRES', 'SCEXAO', 'REACH']
# These are AO188 instruments
ao_inst = ['AO188', 'IRCS', 'HICIAO', 'K3D', 'CHARIS', 'IRD', 'VAMPIRES',
           'SCEXAO', 'REACH']
# These are auto-guiding instruments
ag_inst = ['MOIRCS', 'FOCAS', 'COMICS', 'HDS', 'SWIMS', 'MIMIZUKU',
           'HSC', 'PFS', 'SUKA']

class PluginError(Exception):
    pass

class Plugin(object):

    def __init__(self, model, view, controller, logger):
        super(Plugin, self).__init__()
        self.model = model
        self.view = view
        self.controller = controller
        self.logger = logger

    def build_gui(self, widget):
        raise PluginError("Subclass should override this method!")

    def start(self):
        raise PluginError("Subclass should override this method!")

    def stop(self):
        # Subclass can override this method, but doesn't have to
        pass

#END
