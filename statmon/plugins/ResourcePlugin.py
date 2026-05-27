#
# T. Inagaki
#
import PlBase
import Resource


class ResourcePlugin(PlBase.Plugin):
    """ Resource water, oil """
    aliases = ['TSCV.WATER', 'TSCV.OIL']

    def build_gui(self, container):
        self.root = container

        self.resource = Resource.ResourceDisplay(logger=self.logger)

        container.add_widget(self.resource, stretch=1)

    def start(self):
        self.controller.register_select('resource', self.update,
                                        self.aliases)

    def update(self, statusDict):
        self.logger.debug('status=%s' %str(statusDict))
        water = statusDict.get(ResourcePlugin.aliases[0])
        oil = statusDict.get(ResourcePlugin.aliases[1])

        try:
            self.resource.update_resource(water=water, oil=oil)
        except Exception as e:
            self.logger.error('error: updating status. %s' %str(e))
