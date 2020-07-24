"""
Testing for transistor models
"""
import unittest
from SemiPy.Physics.Modeling.TwoDFETs.Stanford2D import Stanford2DSModel
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from SemiPy.Devices.Devices.FET.ThinFilmFET import TFT
from physics.value import Value, ureg
from SemiPy.Physics.Modeling.BaseModel import ModelInput


# TODO: Should the extract take in the properties (L, W, oxide, channel) and build the FET or should the user create the FET then give to the Extractor?
class TestStanford2DSModel(unittest.TestCase):

    def test_stanford2dsmodel(self):

        gate_oxide = SiO2(thickness=Value(1.0, ureg.nanometer))
        channel = MoS2(layer_number=1, thickness=Value(0.6, ureg.nanometer))

        fet = TFT(channel=channel, gate_oxide=gate_oxide, length=Value(0.050, ureg.micrometer),
                  width=Value(0.05, ureg.micrometer))

        fet.Vt_avg = Value(0.0, ureg.volt)

        fet.max_mobility = Value(35, ureg.centimeter**2 / (ureg.volt * ureg.second))

        fet.mobility_temperature_exponent = Value(0.0, ureg.dimensionless)

        S2DModel = Stanford2DSModel(FET=fet)

        Vds = ModelInput(0, 1.0, num=100, unit=ureg.volt)

        Vgs = ModelInput(0.2, 1.0, num=5, unit=ureg.volt)

        S2DModel.model_output(Vds, Vgs, ambient_temperature=Value(300, ureg.kelvin))



# if __name__ == '__main__':
#     test = TestFETExtractors()
#     test.test_fetextraction()

