"""
Base class for all 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import ThinFilm


class TwoDMaterial(ThinFilm):

    layer_number = None

    single_layer_thickness = None

    def __init__(self, thickness=None, layer_number=None, *args, **kwargs):

        # check if either the layer_number or thickness where given.
        if thickness is not None and layer_number is None:
            self.layer_number = int(thickness / self.single_layer_thickness)

        elif thickness is None and layer_number is not None:
            thickness = layer_number * self.single_layer_thickness
            # save the number of layers
            self.layer_number = layer_number

        super(TwoDMaterial, self).__init__(*args, **kwargs, thickness=thickness)

