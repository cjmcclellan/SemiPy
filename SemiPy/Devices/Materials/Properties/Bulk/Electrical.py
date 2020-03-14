"""
This module contains classes of bulk electrical properties, i.e. resistivity
"""
from SemiPy.Devices.PhysicalProperty import PhysicalProperty
from physics.value import ureg


class ElectricalResistivity(PhysicalProperty):

    prop_name = 'ElectricalResistivity'
    prop_dimensionality = ureg.ohm / ureg.meter

    input_value_names = ['n']
    input_dimensionalities = [ureg.meter ** -2]

    optional_input_value_names = ['temperature']
    optional_input_dimensionalities = [ureg.kelvin]


class ElectricalSheetResistance(PhysicalProperty):

    prop_name = 'ElectricalSheetResistance'
    prop_dimensionality = ureg.ohm

    input_value_names = ['n']
    input_dimensionalities = [ureg.meter ** -2]

    optional_input_value_names = ['temperature']
    optional_input_dimensionalities = [ureg.kelvin]


class BandGap(PhysicalProperty):

    prop_name = 'BandGap'
    prop_dimensionality = ureg.electron_volt

    optional_input_value_names = ['temperature']
    optional_input_dimensionalities = [ureg.kelvin]


class RelativePermittivity(PhysicalProperty):

    prop_name = 'RelativePermittivity'
    prop_dimensionality = ureg.dimensionless


class ElectronMass(PhysicalProperty):

    prop_name = 'ElectronMass'
    prop_dimensionality = ureg.kilogram


class HoleMass(PhysicalProperty):

    prop_name = 'ElectronMass'
    prop_dimensionality = ureg.kilogram

