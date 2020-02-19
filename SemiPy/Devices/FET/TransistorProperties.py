"""
This module contains device properties of transistors, such as maximum on current and minimum off current
"""
from SemiPy.Devices.BaseDevice import DeviceProperty
from physics.units import ureg
from physics.value import Value


class Voltage(DeviceProperty):

    prop_name = 'Voltage'
    prop_dimensionality = ureg.volt


class FETProperty(DeviceProperty):

    input_value_names = ['Vd', 'Vg']
    input_dimensionalities = [ureg.volt, ureg.volt]

    optional_input_value_names = ['n', 'temperature', 'field']
    optional_input_dimensionalities = [ureg.meter ** -2, ureg.kelvin, ureg.volt / ureg.meter]


class CurrentDensity(FETProperty):

    prop_name = 'Current'
    prop_dimensionality = ureg.amp / ureg.meter


class Transconductance(FETProperty):

    prop_name = 'Transconductance'
    prop_dimensionality = 1 / (ureg.ohm * ureg.meter)


class SubthresholdSwing(FETProperty):

    prop_name = 'Subthreshold Swing'
    prop_dimensionality = ureg.amp / (ureg.volt * ureg.meter)


