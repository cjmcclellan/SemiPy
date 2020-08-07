"""
Module for TMD 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from SemiPy.Devices.Materials.TwoDMaterials.TwoDMaterial import TwoDMaterial
from SemiPy.Documentation.ScientificPaper import citation_decorator
from SemiPy.Documentation.Papers.TwoDPapers.TwoDMaterialPapers import MonolayerMoS2ThicknessDickinson,\
    MonolayerMoS2ThermalConductivityYan
import SemiPy.Devices.Materials.Properties as matprop
from physics.value import Value, ureg


class Silicon(Semiconductor):
    """
    The semiconductor material Silicon
    """
    # relative_permittivity = matprop.Bulk.Electrical.RelativePermittivity(value=Value(4.2, ureg.dimensionless))

    thermal_conductivity = matprop.Bulk.Thermal.ThermalConductivity(value=Value(140, ureg.watt/(ureg.kelvin*ureg.meter)),
                                                                    input_values={'temperature': Value(300, ureg.kelvin)})

    # saturation_velocity = matprop.Bulk.Electrical.SaturationVelocity(value=Value(3.4e6, ureg.centimeter/ureg.seconds),
    #                                                                  input_values={'temperature': Value(300, ureg.kelvin)})

    def __init__(self, *args, **kwargs):
        super(Semiconductor, self).__init__(*args, **kwargs)
