"""
This module contains device properties of transistors, such as maximum on current and minimum off current
"""
from SemiPy.Devices.PhysicalProperty import PhysicalProperty
from physics.units import ureg
from physics.value import Value


class FETProperty(PhysicalProperty):

    input_value_names = ['Vd', 'Vg']
    input_dimensionalities = [ureg.volt, ureg.volt]

    optional_input_value_names = ['n', 'temperature', 'field']
    optional_input_dimensionalities = [ureg.meter ** -2, ureg.kelvin, ureg.volt / ureg.meter]


class CurrentDensity(FETProperty):

    prop_name = 'Current'
    prop_dimensionality = ureg.amp / ureg.meter
    prop_standard_units = ureg.microamp / ureg.micrometer


class Mobility(FETProperty):

    prop_name = 'Mobility'
    prop_dimensionality = ureg.meter * ureg.meter / (ureg.volt * ureg.second)
    prop_standard_units = ureg.centimeter ** 2 / ureg.volt / ureg.second


class SubthresholdSwing(FETProperty):

    prop_name = 'Subthreshold Swing'
    prop_dimensionality = ureg.meter * ureg.volt / ureg.amp
    prop_standard_units = ureg.meter * ureg.millivolt / ureg.amp


class Transconductance(FETProperty):

    prop_name = 'Transconductance'
    prop_dimensionality = 1 / (ureg.ohm * ureg.meter)
    prop_standard_units = ureg.microsiemens / ureg.micrometer


