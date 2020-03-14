"""
This module contains properties of thermal interfaces, i.e. thermal contact resistance
"""
from SemiPy.Devices.PhysicalProperty import PhysicalProperty
from physics.value import ureg


class ThermalBoundaryConductance(PhysicalProperty):

    prop_name = 'ThermalBoundaryConductance'
    prop_dimensionality = ureg.watt / (ureg.meter * ureg.meter * ureg.kelvin)

    input_value_names = ['temperature']
    input_dimensionalities = [ureg.kelvin]


