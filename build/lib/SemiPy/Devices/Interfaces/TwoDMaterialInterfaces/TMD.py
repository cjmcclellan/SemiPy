"""
Module for TMD 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from SemiPy.Documentation.Papers.TwoDPapers.TwoDMaterialPapers import MoS2SiO2AlNThermalBoundaryResistance
import SemiPy.Devices.Materials.Properties as matprop
from physics.value import Value, ureg
from SemiPy.Devices.Interfaces.Interface import BaseInterface


class MoS2SiO2(BaseInterface):
    """
    The MoS2 SiO2 interface.
    """
    material1 = MoS2
    material2 = SiO2

    thermal_boundary_conductance = matprop.Interfaces.Thermal.ThermalBoundaryConductance(value=Value(15e6, ureg.watt / (ureg.kelvin * ureg.meter**2)),
                                                                                        cited=True,
                                                                                        input_values={'temperature': Value(300, ureg.kelvin)},
                                                                                        citation=MoS2SiO2AlNThermalBoundaryResistance())

