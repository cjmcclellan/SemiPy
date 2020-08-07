"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.TLM.TLMExtractor import TLMExtractor
from SemiPy.Devices.Devices.FET.ThinFilmFET import nTFT
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from physics.value import Value, ureg
import numpy as np


class TestTLMExtractors(unittest.TestCase):

    def test_tlmextraction(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/TLMExampleData'
        #idvg_path = '../../SampleData/TLMExampleDataShort'
        # idvg_path = '/Users/maisylam/Documents/Stanford_SURF/PycharmProjects/SemiPy/SemiPy/SampleData/TLMExampleData/'

        idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        widths = Value(4.0, ureg.micrometer)
        lengths = Value.array_like(np.array([0.5, 1.0, 2.0, 2.5, 3.0, 3.5]), unit=ureg.micrometer)
        #lengths = Value.array_like(np.array([1.0, 2.0, 0.5]), unit=ureg.micrometer)
        #lengths = Value.array_like(np.array([2.0, 0.5, 1.0]), unit=ureg.micrometer)

        gate_oxide = SiO2(thickness=Value(30, ureg.nanometer))
        channel = MoS2(layer_number=1)
        result = TLMExtractor(widths=widths, lengths=lengths, gate_oxide=gate_oxide, channel=channel, FET_class=nTFT,
                              idvg_path=idvg_path, vd_values=[1.0, 2.0])

        result.save_tlm_plots()

        a = 5


# if __name__ == '__main__':
#     test = TestFETExtractors()
#     test.test_fetextraction()

