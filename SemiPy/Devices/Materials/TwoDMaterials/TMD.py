"""
Module for TMD 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from SemiPy.Devices.Materials.TwoDMaterials.TwoDMaterial import TwoDMaterial
from SemiPy.Documentation.ScientificPaper import citation_decorator
from SemiPy.Documentation.Papers.TwoDPapers.TwoDMaterialPapers import MoS2Thickness
import SemiPy.Devices.Materials.Properties as matprop
from physics.value import Value, ureg


@citation_decorator(MoS2Thickness)
class MoS2(TwoDMaterial, Semiconductor):
    """
    The material MoS2.  Single layer thickness is 0.615 nm taken from <citation>.
    """
    single_layer_thickness = Value(value=0.615, unit=ureg.nanometer)

    relative_permittivity = matprop.Bulk.Electrical.RelativePermittivity(value=Value(4.2, ureg.dimensionless))

    thermal_conductivity = matprop.Bulk.Thermal.ThermalConductivity(value=Value(90, ureg.watt/(ureg.kelvin*ureg.meter)),
                                                                    input_values={'temperature': Value(300, ureg.kelvin)})

    saturation_velocity = matprop.Bulk.Electrical.SaturationVelocity(value=Value(3.4e6, ureg.centimeter/ureg.seconds),
                                                                     input_values={'temperature': Value(300, ureg.kelvin)})

    layer_thickness = matprop.Bulk.Basic.Thickness(value=Value(0.6, ureg.nanometer))

    def __init__(self, *args, **kwargs):
        super(MoS2, self).__init__(*args, **kwargs)


@citation_decorator(MoS2Thickness)
class WS2(TwoDMaterial, Semiconductor):
    """
    The material MoS2.  Single layer thickness is 0.615 nm taken from <citation>.
    """
    single_layer_thickness = Value(value=0.615, unit=ureg.nanometer)

    def __init__(self, *args, **kwargs):
        super(WS2, self).__init__(*args, **kwargs)
