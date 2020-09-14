"""
Testing for transistor models
"""
import unittest
from SemiPy.Physics.Modeling.TwoDFETs.Stanford2D import Stanford2DSModel
from SemiPy.Devices.Materials.TwoDMaterials.TMD import MoS2
from SemiPy.Devices.Materials.Oxides.MetalOxides import SiO2
from SemiPy.Devices.Materials.Semiconductors.BulkSemiconductors import Silicon
from SemiPy.Devices.Devices.FET.ThinFilmFET import TFT
from physics.value import Value, ureg
from SemiPy.Physics.Modeling.BaseModel import ModelInput
import matplotlib.pyplot as plt
import numpy as np


class TestBasic2DFET(unittest.TestCase):

    def test_2DFETExtraction_and_stanford2dsmodel(self):

        gate_oxide = SiO2(thickness=Value(30.0, ureg.nanometer))
        channel = MoS2(layer_number=1, thickness=Value(0.6, ureg.nanometer))
        substrate = Silicon()

        fet = TFT(channel=channel, gate_oxide=gate_oxide, length=Value(50, ureg.nanometer),
                  width=Value(0.05, ureg.micrometer), substrate=substrate)

        fet.Vt_avg.set(Value(0.19, ureg.volt))

        fet.Rc.set(Value(100.0, ureg.ohm * ureg.micrometer),
                   input_values={'n': Value(1e13, ureg.centimeter**-2)})

        fet.max_mobility.set(Value(40, ureg.centimeter**2 / (ureg.volt * ureg.second)),
                             input_values={'Vd': Value(1, ureg.volt), 'Vg': Value(1, ureg.volt)})

        fet.mobility_temperature_exponent.set(Value(1.15, ureg.dimensionless))

        S2DModel = Stanford2DSModel(FET=fet)

        Vds = ModelInput(0.4, 1.2, num=3, unit=ureg.volt)

        Vgs = ModelInput(0.0, 1.0, num=70, unit=ureg.volt)

        temps = [290, 400]
        linestyles = ['-', '--']

        # temps = [310]
        #for temp, linestyle in zip(temps, linestyles):
         #   S2DModel.model_output(Vds, Vgs, heating=True, vsat=True,
          #                        ambient_temperature=Value(temp, ureg.kelvin), linestyle=linestyle)

        #plt.savefig('IdVd_plot_at')
        #plt.show()

        #S2DModel.compute_quantum_cap(295, 1)
        #S2DModel.compute_diffusion_current(295, .1, 0.4)


        vg_array = np.arange(0, 0.4, 0.01)
        vd_array = np.arange(.4, 1.2, 0.4)
        S2DModel.plot_diffusion_current(295,  vg_array, vd_array)


        vg_array = np.arange(-0, 1.01, 0.01)
        #S2DModel.compute_quantum_cap_array(295, vg_array)


