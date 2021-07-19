"""
Testing for transistor models
"""
import unittest
from SemiPy.Datasets.IVDataset import IdVdDataSet, IdVgDataSet
from physics.value import Value, ureg
from SemiPy.helper.paths import get_abs_semipy_path


class TestIVDataSets(unittest.TestCase):

    def test_idvgdataset(self):

        path = get_abs_semipy_path('SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt')

        dataset = IdVgDataSet(data_path=path)

        result = dataset.get_column(column_name='vg_fwd', master_independent_value_range=[0, 10.0])

        self.assertEqual(result[0][0], Value(0.0, ureg.volt), 'Error in the IdVgDataSet object get column function when requesting master'
                                                              ' independent value range.  Lowest Vg value should be 0.0 volt but is {0}'.format(result[0][0]))

        self.assertEqual(result[0][-1], Value(9.5, ureg.volt), 'Error in the IdVgDataSet object get column function when requesting master'
                                                              ' independent value range.  Highest Vg value should be 9.5 volt but is {0}'.format(result[0][-1]))

        result, vd = dataset.get_column(column_name='id', return_set_values=True)

        self.assertEqual(result[0][-1], Value(1.921e-6, ureg.amp), 'Error in the IdVgDataSet object get column function. Highest Id value should '
                                                                'be 1.921e-6 amps but is {0}'.format(result[0][-1]))

        self.assertEqual(vd[-1], Value(2.0, ureg.volt), 'Error in the IdVgDataSet object get column function. Highest Vd value should '
                                                                'be 2.0 volts but is {0}'.format(result[0][-1]))

        result = dataset.get_column_set(column_name='id', secondary_value=Value(1.0, ureg.volt))

        self.assertEqual(len(result.shape), 1, 'Error in the IdVgDataSet object get column set function. Result should only have '
                                               '1 dimension but it has {0}'.format(len(result.shape)))

