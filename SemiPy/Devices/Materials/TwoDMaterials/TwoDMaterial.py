"""
Base class for all 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import ThinFilm


class TwoDMaterial(ThinFilm):

    layer_number = None

    def __init__(self, layer_number, *args, **kwargs):

        super(TwoDMaterial, self).__init__(*args, **kwargs)

        # save the number of layers
        self.layer_number = layer_number
