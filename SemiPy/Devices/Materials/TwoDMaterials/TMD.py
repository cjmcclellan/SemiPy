"""
Module for TMD 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from SemiPy.Devices.Materials.TwoDMaterials.TwoDMaterial import TwoDMaterial


class MoS2(TwoDMaterial, Semiconductor):

    def __init__(self, *args, **kwargs):
        super(MoS2, self).__init__(*args, **kwargs)
