"""
Testing for transistor models
"""
import unittest
from Extractions.Datasets.IVDataset import IdVdDataSet


class TestTransistor(unittest.TestCase):

    def test_transistor(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/src/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'

        dataset = IdVdDataSet(data_path=path)

        result, vd = dataset.get_column(column_name='id', return_set_values=True)

        result = dataset.get_column_set(column_name='id', secondary_value=-20)

        a = 5


if __name__ == '__main__':
    test = TestTransistor()
    test.test_transistor()

