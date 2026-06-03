#
# T. Inagaki
#
from ginga.gw import Widgets

import PlBase
from CustomLabel import Label


class Resource(Label):
    ''' Water/Oil Storage'''
    def __init__(self, parent=None, logger=None):
        super( Resource, self).__init__(parent=parent, fs=10, width=275,
                                        height=25, align='vcenter',
                                        weight='bold', logger=logger)

    def update_resource(self,  resource):
        ''' resource= TSCV.WATER | TSCV.OIL  '''

        self.logger.debug(f'resource={resource}')

        color = self.normal

        if resource == 0:
            text = 'Normal'
        elif resource >= 1.0:
            text = 'HIGH ALARM'
            color = self.alarm
        elif resource <= -1.0:
            text = 'LOW ALARM'
            color = self.alarm
        else:
            text = 'Undefined'
            color = self.alarm

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class WaterStorageDisplay(Widgets.HBox):
    ''' WaterStorage  '''
    def __init__(self, parent=None, logger=None):
        super().__init__()
        self.set_spacing(0)
        self.set_margins(0, 0, 0, 0)

        self.water_label = Label(parent=parent, fs=10, width=175,
                                 height=25, align='vcenter', weight='bold',
                                 logger=logger)

        self.water_label.set_text('Water Storage')
        #self.water_label.setIndent(15)

        self.water = Resource(parent=parent, logger=logger)
        self.__set_layout()

    def __set_layout(self):
        self.add_widget(self.water_label)
        self.add_widget(self.water)

    def update_water(self, water):
        self.water.update_resource(resource=water)


class OilStorageDisplay(Widgets.HBox):
    def __init__(self, parent=None, logger=None):
        super().__init__()
        self.set_spacing(0)
        self.set_margins(0, 0, 0, 0)

        self.oil_label = Label(parent=parent, fs=10, width=175,
                               height=25, align='vcenter', weight='bold',
                               logger=logger)

        self.oil_label.set_text('Oil Storage')
        #self.oil_label.setIndent(15)

        self.oil = Resource(parent=parent, logger=logger)
        self.__set_layout()

    def __set_layout(self):
        self.add_widget(self.oil_label)
        self.add_widget(self.oil)

    def update_oil(self, oil):
        self.oil.update_resource(resource=oil)


class ResourceDisplay(Widgets.VBox):
    def __init__(self, parent=None, logger=None):
        super().__init__()
        self.set_spacing(1)
        self.set_margins(0, 0, 0, 0)

        self.water = WaterStorageDisplay(parent=parent, logger=logger)
        self.oil = OilStorageDisplay(parent=parent, logger=logger)

        self.__set_layout()

    def __set_layout(self):
        self.add_widget(self.water)
        self.add_widget(self.oil)

    def update_resource(self, water, oil):
        self.water.update_water(water=water)
        self.oil.update_oil(oil=oil)


class ResourcePlugin(PlBase.Plugin):
    """ Resource water, oil """
    aliases = ['TSCV.WATER', 'TSCV.OIL']

    def build_gui(self, container):
        self.root = container

        self.resource = ResourceDisplay(logger=self.logger)

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
