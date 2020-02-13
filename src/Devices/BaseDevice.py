"""
Holds the BaseDevice class for all Device classes
"""
import csv
import os
from physics.units import ureg
from physics.value import Value


class BaseDevice(object):

    def __init__(self, name='basedevice'):
        """
        The base class for all devices
        Args:
            name (str): The name of the BaseDevice instance
        """
        # properties to publish for saving as a csv
        self.publish_prop = []

        # # name of the device
        assert isinstance(name, str), 'The name of the device must be a string.'
        self.name = name

    def _add_publish_property(self, name):
        self.publish_prop.append(name)

    def publish_csv(self, path):
        """

        Args:
            path (str): Path to the where the data should be saved.

        Returns:

        """
        assert isinstance(path, str), 'path must be a string.'
        path = os.path.join(path, self.name + '.csv')
        with open(path, 'w') as f:
            for key in self.publish_prop:
                prop = self.__dict__[key]
                # prop = self.publish_prop[key]
                if isinstance(prop, Value):
                    f.write("%s,%s,%s\n" % (key, prop.value, prop.unit))
                else:
                    f.write("%s,%s\n" % (key, prop))
