"""
This module contains the Base Material class for all Materials
"""
import SemiPy.Devices.Materials.Properties.Bulk.Electrical as mpbe
from physics.fundamental_constants import free_space_permittivity_F_div_cm
from physics.value import Value, ureg


class BaseMaterial(object):

    properties = []

    relative_permittivity = None

    capacitance = None


class Semiconductor(BaseMaterial):

    bandgap = None

    electron_mass = None

    hole_mass = None


class ThinFilm(BaseMaterial):

    thickness = None

    def __init__(self, thickness, *args, **kwargs):
        self.thickness = thickness
        # with the thickness, compute the capacitance
        self.capacitance = (free_space_permittivity_F_div_cm * self.relative_permittivity.value / self.thickness).adjust_unit(
            ureg.farad / (ureg.centimeter ** 2))
