"""
Testing for transistor models
"""
import unittest
from .IVDataset import IVDataSet


class TestTransistor(unittest.TestCase):

    def test_transistor(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'

        IVDataSet(data_path=path)


if __name__ == '__main__':
    test = TestTransistor()
    test.test_transistor()

