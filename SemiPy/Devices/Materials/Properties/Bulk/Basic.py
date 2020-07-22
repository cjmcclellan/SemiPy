"""
This module contains classes of basic bulk properties, i.e. thickness
"""
from SemiPy.Devices.PhysicalProperty import PhysicalProperty
from physics.value import ureg


class Thickness(PhysicalProperty):

    prop_name = 'Thickness'
    prop_dimensionality = ureg.meter
