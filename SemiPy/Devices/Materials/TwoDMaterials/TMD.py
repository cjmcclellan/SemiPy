"""
Module for TMD 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from SemiPy.Devices.Materials.TwoDMaterials.TwoDMaterial import TwoDMaterial
import SemiPy.Devices.Materials.Properties as matprop
from physics.value import Value, ureg


class MoS2(TwoDMaterial, Semiconductor):

    relative_permittivity = matprop.Bulk.Electrical.RelativePermittivity(value=Value(4.2, ureg.dimensionless))

    thermal_conductivity = matprop.Bulk.Thermal.ThermalConductivity(value=Value(30, ureg.watt/(ureg.kelvin*ureg.meter)),
                                                                    input_values={'temperature': Value(300, ureg.kelvin)})

    saturation_velocity = matprop.Bulk.Electrical.SaturationVelocity(value=Value(3.4e6, ureg.centimeter/ureg.seconds),
                                                                     input_values={'temperature': Value(300, ureg.kelvin)})

    layer_thickness = matprop.Bulk.Basic.Thickness(value=Value(0.6, ureg.nanometer))

    def __init__(self, *args, **kwargs):
        super(MoS2, self).__init__(*args, **kwargs)
