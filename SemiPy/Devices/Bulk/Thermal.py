"""
This module contains properties of thermal interfaces, i.e. thermal contact resistance
"""
from SemiPy.Devices.BaseDevice import DeviceProperty
from physics.value import ureg


class ThermalBoundaryConductance(DeviceProperty):

    prop_name = 'ThermalBoundaryConductance'
    prop_dimensionality = ureg.watt / (ureg.meter * ureg.meter * ureg.kelvin)

    input_value_names = ['temperature']
    input_dimensionalities = [ureg.kelvin]


