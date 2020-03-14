"""
Base class for all 2D Materials
"""
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor, ThinFilm
import SemiPy.Devices.Materials.Properties as matprop
from physics.value import Value, ureg


class MetalOxide(Semiconductor, ThinFilm):
    pass


class Al2O3(MetalOxide):

    bandgap = matprop.Bulk.Electrical.BandGap(value=Value(7.5, unit=ureg.electron_volt))

    relative_permittivity = matprop.Bulk.Electrical.RelativePermittivity(value=Value(8.5, ureg.dimensionless))


class SiO2(MetalOxide):

    bandgap = matprop.Bulk.Electrical.BandGap(value=Value(8.6, unit=ureg.electron_volt))

    relative_permittivity = matprop.Bulk.Electrical.RelativePermittivity(value=Value(3.9, ureg.dimensionless))
