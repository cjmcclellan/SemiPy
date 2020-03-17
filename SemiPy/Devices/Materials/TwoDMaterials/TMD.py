"""
Module for TMD 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from SemiPy.Devices.Materials.TwoDMaterials.TwoDMaterial import TwoDMaterial
from SemiPy.Documentation.ScientificPaper import citation_decorator
from SemiPy.Documentation.Papers.TwoDPapers.TwoDMaterialPapers import MoS2Thickness
from physics.value import Value, ureg


@citation_decorator(MoS2Thickness)
class MoS2(TwoDMaterial, Semiconductor):
    """
    The material MoS2.  Single layer thickness is 0.615 nm taken from <citation>.
    """
    single_layer_thickness = Value(value=0.615, unit=ureg.nanometer)

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
