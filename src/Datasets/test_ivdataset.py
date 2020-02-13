"""
Testing for transistor models
"""
import unittest
from .IVDataset import IdVdDataSet


class TestTransistor(unittest.TestCase):

    def test_transistor(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'

        dataset = IdVdDataSet(data_path=path)

        result = dataset.get_column_set(column_name='vd', secondary_value=-20)

        a = 5


if __name__ == '__main__':
    test = TestTransistor()
    test.test_transistor()

