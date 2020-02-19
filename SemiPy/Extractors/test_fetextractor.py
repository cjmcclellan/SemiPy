"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.FETExtractor import FETExtractor


class TestFETExtractor(unittest.TestCase):

    def test_fetextraction(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        # idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/Extractions/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/Extractions/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'

        idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'

        result = FETExtractor(width=1, length=1, tox=30, epiox=3.9,
                              device_polarity='p', idvg_path=idvg_path, idvd_path=idvd_path)



        a = 5


if __name__ == '__main__':
    test = TestFETExtractor()
    test.test_fetextraction()

