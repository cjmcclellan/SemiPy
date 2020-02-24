"""
Testing for transistor models
"""
import unittest
from SemiPy.Datasets.IVDataset import IdVdDataSet, IdVgDataSet
from physics.value import Value, ureg


class TestTransistor(unittest.TestCase):

    def test_transistor(self):

        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/src/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'

        dataset = IdVgDataSet(data_path=path)

        result = dataset.get_column(column_name='vg_fwd', master_independent_value_range=[0, 18.0])

        result, vd = dataset.get_column(column_name='id', return_set_values=True)

        result = dataset.get_column_set(column_name='id', secondary_value=Value(1.0, ureg.volt))

        a = 5


if __name__ == '__main__':
    test = TestTransistor()
    test.test_transistor()

