"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor


class TestFETExtractors(unittest.TestCase):

    def test_fetextraction(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        #
        # idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'

        result = FETExtractor(width=1, length=1, tox=30, epiox=3.9,
                              device_polarity='n', idvg_path=idvg_path, idvd_path=idvd_path)

        result.FET.publish_csv('.')


        result.save_plots()
        print(result.FET.max_gm)
        print(result.FET.min_ss)
        a = 5


# if __name__ == '__main__':
#     test = TestFETExtractors()
#     test.test_fetextraction()

