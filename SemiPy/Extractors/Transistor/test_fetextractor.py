"""
Testing for transistor models
"""
import unittest
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2, aIGZO
from SemiPy.Devices.Materials.Semiconductors.BulkSemiconductors import Silicon
from SemiPy.Devices.Devices.FET.ThinFilmFET import nTFT, pTFT, aTFT
from SemiPy.helper.paths import get_abs_semipy_path

from physics.value import Value, ureg

import plotly

# TODO: Should the extractor take in the properties (L, W, oxide, channel) and build the FET or should the user create the FET then give to the Extractor?


class TestFETExtractors(unittest.TestCase):

    def test_fetextraction(self):

        # plotly.io.orca.config.executable = '/node_modules/orca/bin/orca'
        idvd_path = get_abs_semipy_path('SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt')
        idvg_path = get_abs_semipy_path('SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt')
        # path = '/home/connor/Documents/Stanford_Projects/Extractions/src/SampleData/FETExampleData/nano_patterning.csv'
        # idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        # idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        #
        #idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        #idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'
        #idvd_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt'
        #idvg_path = '/home/connor/Documents/Stanford_Projects/Extractions/fetextraction/SemiPy/SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt'

        gate_oxide = SiO2(thickness=Value(30, ureg.nanometer))
        channel = MoS2(layer_number=1)
        substrate = Silicon()

        fet = nTFT(gate_oxide=gate_oxide, channel=channel, width=Value(1, ureg.micrometer), substrate=substrate,
                   length=Value(1, ureg.micrometer))

        # SchottkyModel(fet, )

        result = FETExtractor(FET=fet, idvg_path=idvg_path, idvd_path=idvd_path)
        print(result.FET.Vt_avg)
        print(result.FET.Vt_fwd)
        print(result.FET.Vt_bwd)
        print(result.FET.min_ss)

        # nFET data
        self.assert_value_equals(result.FET.Vt_avg, Value(3.78, ureg.volt), 'Vt avg')
        self.assert_value_equals(result.FET.Vt_bwd, Value(4.06, ureg.volt), 'Vt bwd')
        self.assert_value_equals(result.FET.Vt_fwd, Value(3.5, ureg.volt), 'Vt fwd')
        self.assert_value_equals(result.FET.min_ss, Value(534.15, ureg.micrometer * ureg.millivolt / ureg.ampere), 'min SS')
        self.assert_value_equals(result.FET.max_gm, Value(3.64, ureg.microsiemens / ureg.micrometer), 'Max Gm')
        self.assert_value_equals(result.FET.max_mobility, Value(15.82, ureg.centimeter ** 2 / ureg.second / ureg.volt), 'Max Mobility')

        fet = pTFT(gate_oxide=gate_oxide, channel=channel, width=Value(1, ureg.micrometer),
                   length=Value(1, ureg.micrometer),
                   substrate=substrate)

        result = FETExtractor(FET=fet, idvg_path=idvg_path, idvd_path=idvd_path)
        print(result.FET.min_ss)
        # pFET data
        # self.assert_value_equals(result.FET.Vt_avg, Value(-15.88, ureg.volt), 'Vt avg')
        # self.assert_value_equals(result.FET.Vt_bwd, Value(-14.96, ureg.volt), 'Vt bwd')
        # self.assert_value_equals(result.FET.Vt_fwd, Value(-16.81, ureg.volt), 'Vt fwd')
        # self.assert_value_equals(result.FET.max_gm, Value(-0.8, ureg.microsiemens / ureg.micrometer), 'Max Gm')
        # self.assert_value_equals(result.FET.min_ss, Value(482.5, ureg.meter * ureg.millivolt / ureg.ampere), 'min SS')
        # self.assert_value_equals(result.FET.max_mobility, Value(15.82, ureg.centimeter ** 2 / ureg.second / ureg.volt), 'Max Mobility')

        # result.FET.publish_csv('.')

        # result.save_plots()

    def test_igzo(self):
        # This test models an a-IGZO device with 20nm IGZO, 100nm SiO2 on Si substrate.
        # Documentation notes:
            # 1. Add material and copy material properties
            # 2. Set model in unittest
            # 3. Files

        # TODO: Change filepaths to point correctly
        idvd_path = get_abs_semipy_path('SampleData/FETExampleData/WSe2_Sample_4_Id_Vd.txt')
        idvg_path = get_abs_semipy_path('SampleData/FETExampleData/WSe2_Sample_4_Id_Vg.txt')

        gate_oxide = SiO2(thickness=Value(100, ureg.nanometer))
        channel = aIGZO(thickness=Value(20, ureg.nanometer))
        substrate = Silicon()

        fet = pTFT(gate_oxide=gate_oxide, channel=channel, width=Value(180, ureg.micrometer), substrate=substrate,
                   length=Value(30, ureg.micrometer))

        result = FETExtractor(FET=fet, idvg_path=idvg_path, idvd_path=idvd_path)
        print(result.FET.max_gm)
        print(result.FET.max_mobility)
        print(result.FET.Vt_avg)
        print(result.FET.min_ss)
        

    def assert_value_equals(self, result_value, true_value, value_name):

        # test the value equals. result_value should be of type PhysicalProperty, so check the value property
        self.assertAlmostEqual(result_value.magnitude, true_value, 1,  'Error in the FET extractor. The {0} should be {1} but it is {2}'
                         .format(value_name, true_value, result_value))
