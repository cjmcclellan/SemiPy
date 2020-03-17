"""
This module contains properties of thermal interfaces, i.e. thermal contact resistance
"""
from SemiPy.Devices.PhysicalProperty import PhysicalProperty
from physics.value import ureg


class ThermalConductivity(PhysicalProperty):

    prop_name = 'ThermalConductivity'
    prop_dimensionality = ureg.watt / (ureg.meter * ureg.kelvin)

    input_value_names = ['temperature']
    input_dimensionalities = [ureg.kelvin]


