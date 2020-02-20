"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.TLM.TLMExtractor import TLMExtractor
from physics.value import Value, ureg


class TestTLMExtractors(unittest.TestCase):

    def test_tlmextraction(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/TLMExampleData'

        # idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        widths = Value(1.0, ureg.micrometer)
        lengths = Value(1.0, ureg.micrometer)
        tox = Value(30, ureg.nanometer)

        result = TLMExtractor(widths=widths, lengths=lengths, tox=tox, epiox=3.9,
                              device_polarity='n', idvg_path=idvg_path,
                              vd_values=[1.0, 2.0])



        a = 5


if __name__ == '__main__':
    test = TestFETExtractors()
    test.test_fetextraction()

