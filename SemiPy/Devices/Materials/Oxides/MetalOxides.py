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

    thermal_conductivity = matprop.Bulk.Thermal.ThermalConductivity(value=Value(1, ureg.watt/(ureg.kelvin*ureg.meter)),
                                                                    input_values={'temperature': Value(300, ureg.kelvin)})


class aIGZO(MetalOxide):
    bandgap = matprop.Bulk.Electrical.BandGap(value=Value(3.2, unit=ureg.electron_volt))

    relative_permittivity = matprop.Bulk.Electrical.RelativePermittivity(value=Value(3.9, ureg.dimensionless))

    thermal_conductivity = matprop.Bulk.Thermal.ThermalConductivity(value=Value(1.4, ureg.watt/(ureg.kelvin*ureg.meter)),
                                                                    input_values={'temperature': Value(300, ureg.kelvin)})