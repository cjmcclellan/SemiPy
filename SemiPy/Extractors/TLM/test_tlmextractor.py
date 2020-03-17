"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.TLM.TLMExtractor import TLMExtractor
from physics.value import Value, ureg
import numpy as np


class TestTLMExtractors(unittest.TestCase):

    def test_tlmextraction(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/TLMExampleData'
        idvg_path = '../../SampleData/TLMExampleDataShort'

        # idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        widths = Value(4.0, ureg.micrometer)
        # lengths = Value.array_like(np.array([0.5, 1.0, 2.0, 2.5, 3.0, 3.5]), unit=ureg.micrometer)
        # lengths = Value.array_like(np.array([1.0, 0.5, 2.0]), unit=ureg.micrometer)
        tox = Value(90, ureg.nanometer)

        result = TLMExtractor(widths=widths, lengths=lengths, tox=tox, epiox=3.9,
                              device_polarity='n', idvg_path=idvg_path,
                              vd_values=[1.0, 2.0])

        result.save_tlm_plots()

        a = 5


# if __name__ == '__main__':
#     test = TestFETExtractors()
#     test.test_fetextraction()

