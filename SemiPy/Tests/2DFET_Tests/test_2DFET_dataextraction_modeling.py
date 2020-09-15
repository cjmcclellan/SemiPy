"""
Testing for transistor models
"""
import unittest
from SemiPy.Physics.Modeling.TwoDFETs.Stanford2D import Stanford2DSModel
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from SemiPy.Devices.Materials.Semiconductors.BulkSemiconductors import Silicon
from SemiPy.Devices.Devices.FET.ThinFilmFET import nTFT
from physics.value import Value, ureg
from SemiPy.Physics.Modeling.BaseModel import ModelInput
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
from SemiPy.helper.paths import get_abs_semipy_path
from SemiPy.Plotting.IVPlotting.IVPlot import IdVgPlot, IdVdPlot


class TestBasic2DFET(unittest.TestCase):

    def test_2DFETExtraction_and_stanford2dsmodel(self):

        idvd_path = get_abs_semipy_path('SampleData/FETExampleData/MoS2AlOx/MoS2_15AlOxALD_Id_Vd.csv')
        idvg_path = get_abs_semipy_path('SampleData/FETExampleData/MoS2AlOx/MoS2_15AlOxALD_Id_Vg.txt')

        gate_oxide = SiO2(thickness=Value(30.0, ureg.nanometer))
        channel = MoS2(layer_number=1)
        substrate = Silicon()

        fet = nTFT(channel=channel, gate_oxide=gate_oxide, length=Value(400, ureg.nanometer),
                   width=Value(2.2, ureg.micrometer), substrate=substrate)

        result = FETExtractor(FET=fet, idvg_path=idvg_path, idvd_path=idvd_path)

        fet = result.FET

        fet.Rc.set(Value(480.0, ureg.ohm * ureg.micrometer),
                   input_values={'n': Value(1e13, ureg.centimeter**-2)})

        fet.mobility_temperature_exponent.set(Value(0.85, ureg.dimensionless))

        fet.max_mobility.set(Value(35, ureg.centimeter**2 / (ureg.volt * ureg.second)),
                             input_values={'Vd': Value(1, ureg.volt), 'Vg': Value(1, ureg.volt)})

        S2DModel = Stanford2DSModel(FET=fet)

        Vds = ModelInput(0.0, 5.0, num=40, unit=ureg.volt)
        Vgs = ModelInput(0.0, 30.0, num=4, unit=ureg.volt)

        ambient_temperature = Value(300, ureg.kelvin)

        id = S2DModel.model_output(Vds, Vgs, heating=True, vsat=True, diffusion=False, drift=True,
                                   ambient_temperature=ambient_temperature)

        plot = IdVdPlot('IdVd')

        plot.add_idvd_dataset(result.idvd, marker='o')

        for key in id.keys():
            if 'Id' in key:
                plot.add_data(Vds.range, id[key], linewidth=4.0)

        plot.show_plot()

