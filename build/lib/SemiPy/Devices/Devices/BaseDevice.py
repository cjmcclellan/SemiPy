"""
Holds the BaseDevice class for all Device classes
"""
import csv
import os
from physics.units import ureg
from physics.value import Value
from SemiPy.Devices.PhysicalProperty import PhysicalProperty


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

    # def round_value(self, value):
    #     assert isinstance(value, Value)
    #     value = value.reduced_units()
    #     a = 5

    def publish_csv(self, path):
        """

        Args:
            path (str): Path to the where the data should be saved.

        Returns:

        """
        assert isinstance(path, str), 'path must be a string.'
        path = os.path.join(path, self.name + '.csv')
        with open(path, 'w') as f:
            # first write the column names
            f.write("Property,Value,Unit\n")
            for key in self.publish_prop:
                try:
                    prop = self.__dict__[key]
                except KeyError:
                    prop = getattr(self, key)
                # prop = self.publish_prop[key]
                if isinstance(prop, Value):
                    f.write("%s,%s,%s\n" % (key, prop.magnitude, prop.unit))
                elif isinstance(prop, PhysicalProperty):
                    f.write("%s,%s,%s\n" % (key, prop.value.magnitude, prop.value.unit))
                else:
                    f.write("%s,%s\n" % (key, prop))


class Voltage(PhysicalProperty):

    prop_name = 'Voltage'
    prop_dimensionality = ureg.volt
    prop_standard_units = ureg.volt

#
# class DeviceProperty(object):
#
#     prop_name = None
#     prop_dimensionality = None
#     # the value will be adjusted to the standard units and rounded to two decimal places
#     prop_standard_units = None
#
#     input_value_names = []
#     input_dimensionalities = []
#
#     optional_input_value_names = []
#     optional_input_dimensionalities = []
#
#     def __init__(self, name=None):
#         """
#         DeviceProperty is a object that records a property of a specific electronic device property at
#         a certain input condition.  For example, this could be the on-current of a transistor at a drain voltage of 1 V
#         and gate voltage of 2 V
#         """
#         self.value = None
#         self.input_values = {}
#         # save the name of the property
#         if name is None:
#             self.name = self.prop_name
#         else:
#             assert isinstance(name, str), 'The given name of the property must be a string'
#             self.name = name
#
#     def __getitem__(self, item):
#         """
#         Get any item of this property
#         Args:
#             item (str):
#
#         Returns:
#             Value
#         """
#         if item == self.prop_name:
#             return self.value
#         elif item in self.input_value_names or item in self.optional_input_value_names:
#             return self.input_values[item]
#         else:
#             raise ValueError('The item {0} is not a part of this device property.'.format(item))
#
#     # def __get__(self, instance, owner):
#     #     return self.value
#
#     # def __set__(self, instance, value):
#     #     assert_value(value)
#     #     assert value.unit.dimensionality == self.prop_dimensionality.dimensionality,\
#     #         'Your dimensionality is incorrect for {0}. Yours is {1}, but it should be {2}'.format(self.prop_name,
#     #                                                                                               value.unit.dimensionality,
#     #                                                                                               self.prop_dimensionality.dimensionality)
#     #     self.value = value
#
#     def set(self, value, input_values=None):
#         """
#         Set the property and input values for this Device Property.
#         Args:
#             value (physics.Value): The Value to be set for this property
#             input_values (dict): A dictionary of the input values, using the convention {'input_name': input_value}
#
#         Returns:
#             None
#         """
#         # save the prop value
#         assert_value(value)
#         assert value.unit.dimensionality == self.prop_dimensionality.dimensionality, 'Your dimensionality is incorrect for {0}. Yours is {1}, but it should be' \
#                 ' {2}'.format(self.prop_name, value.unit.dimensionality, self.prop_dimensionality.dimensionality)
#         self.value = value
#
#         # now if the standard units were given, then adjust the value units
#         if self.prop_standard_units is not None:
#             self.value = self.value.adjust_unit(self.prop_standard_units)
#             # now round the value to 2 decimal places
#             self.value = Value(value=round(self.value.value * 100) / 100, unit=self.value.unit)
#
#         # save the input values, making sure that they match the given names
#         for i, input_name in enumerate(self.input_value_names):
#             input_value = input_values.get(input_name, None)
#             assert input_value is not None, 'You are missing the required {0} input for this property'.format(input_name)
#             assert_value(input_value)
#             assert input_value.unit.dimensionality == self.input_dimensionalities[i].dimensionality,\
#                 'Your dimensionality is incorrect for input {0}.  Yours is {1}, but it should be' \
#                 ' {2}'.format(input_name, input_value.unit.dimensionality, self.input_dimensionalities[i].dimensionality)
#
#             self.input_values[input_name] = input_value
#
#         # now go through the optional input values
#         for i, optional_name in enumerate(self.optional_input_value_names):
#             input_value = input_values.get(optional_name, None)
#             if input_value is not None:
#                 assert_value(input_value)
#                 assert input_value.unit.dimensionality == self.input_dimensionalities[i].dimensionality, \
#                     'Your dimensionality is incorrect for input {0}.  Yours is {1}, but it should be' \
#                     ' {2}'.format(optional_name, input_value.unit.dimensionality, self.input_dimensionalities[i].dimensionality)
#
#                 self.input_values[optional_name] = input_value
#
#     def __str__(self):
#         return '{0} = {1}'.format(self.name, self.value)
