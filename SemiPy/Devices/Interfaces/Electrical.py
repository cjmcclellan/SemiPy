"""
This module contains properties of electrical interfaces, i.e. contact resistance
"""
from SemiPy.Devices.BaseDevice import DeviceProperty
from physics.value import ureg


class ElectricalContactResistance(DeviceProperty):

    prop_name = 'ElectricalContactResistance'
    prop_dimensionality = ureg.ohm * ureg.meter

    input_value_names = ['n']
    input_dimensionalities = [ureg.meter ** -2]

    optional_input_value_names = ['temperature']
    optional_input_dimensionalities = [ureg.kelvin]

