"""
This module contains classes of bulk electrical properties, i.e. resistivity
"""
from SemiPy.Devices.BaseDevice import DeviceProperty
from physics.value import ureg


class ElectricalResistivity(DeviceProperty):

    prop_name = 'ElectricalResistivity'
    prop_dimensionality = ureg.ohm / ureg.meter

    input_value_names = ['n']
    input_dimensionalities = [ureg.meter ** -2]

    optional_input_value_names = ['temperature']
    optional_input_dimensionalities = [ureg.kelvin]


class ElectricalSheetResistance(DeviceProperty):

    prop_name = 'ElectricalSheetResistance'
    prop_dimensionality = ureg.ohm

    input_value_names = ['n']
    input_dimensionalities = [ureg.meter ** -2]

    optional_input_value_names = ['temperature']
    optional_input_dimensionalities = [ureg.kelvin]

