"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from physics.value import Value, ureg


# TODO: Should the extract take in the properties (L, W, oxide, channel) and build the FET or should the user create the FET then give to the Extractor?
class TestFETExtractors(unittest.TestCase):

    def test_fetextraction(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        # idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        #
        idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'

        gate_oxide = SiO2(thickness=Value(30, ureg.nanometer))
        channel = MoS2(layer_number=1)

        result = FETExtractor(width=1, length=1, gate_oxide=gate_oxide, channel=channel,
                              device_polarity='n', idvg_path=idvg_path, idvd_path=idvd_path)

        result.FET.publish_csv('.')


        result.save_plots()
        print(result.FET.max_gm)
        print(result.FET.min_ss)
        a = 5


# if __name__ == '__main__':
#     test = TestFETExtractors()
#     test.test_fetextraction()

