"""
Base class for all 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import ThinFilm


class TwoDMaterial(ThinFilm):

    layer_number = None

    layer_thickness = None

    def __init__(self, layer_number, thickness=None, *args, **kwargs):

        if thickness is None:
            assert self.layer_thickness is not None, 'You must provide a thickness for this material.'
            thickness = layer_number * self.layer_thickness.value

        super(TwoDMaterial, self).__init__(thickness, *args, **kwargs)

