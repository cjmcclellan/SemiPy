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
import math


class Test2DFETModels(unittest.TestCase):

    def test_stanford2dsmodel(self):

        gate_oxide = SiO2(thickness=Value(3.0, ureg.nanometer))
        channel = MoS2(layer_number=1, thickness=Value(0.6, ureg.nanometer))
        substrate = Silicon()

        fet = TFT(channel=channel, gate_oxide=gate_oxide, length=Value(50, ureg.nanometer),
                  width=Value(0.05, ureg.micrometer), substrate=substrate)

        fet.Vt_avg.set(Value(0.2, ureg.volt))

        fet.Rc.set(Value(100.0, ureg.ohm * ureg.micrometer),
                   input_values={'n': Value(1e13, ureg.centimeter**-2)})

        fet.max_mobility.set(Value(40, ureg.centimeter**2 / (ureg.volt * ureg.second)),
                             input_values={'Vd': Value(1, ureg.volt), 'Vg': Value(1, ureg.volt)})

        fet.mobility_temperature_exponent.set(Value(1.15, ureg.dimensionless))

        S2DModel = Stanford2DSModel(FET=fet)

        Vds = ModelInput(0.5, 1.0, num=2, unit=ureg.volt)

        Vgs = ModelInput(0.0, 1.0, num=40, unit=ureg.volt)

        temps = [300, 400]
        # linestyles = ['-', '--']

        # temps = [310]
        #for temp, linestyle in zip(temps, linestyles):
        # S2DModel.model_output(Vds, Vgs, heating=True, vsat=True, ambient_temperature=Value(300, ureg.kelvin))

        #plt.savefig('IdVd_plot_at')
        #plt.show()

        #S2DModel.compute_quantum_cap(295, 1)
        #S2DModel.compute_diffusion_current(295, .1, 0.4)
        for t in temps:
            Vds = ModelInput(0.5, 1.0, num=2, unit=ureg.volt)

            Vgs = ModelInput(0.0, 1.0, num=40, unit=ureg.volt)
            idrift = S2DModel.model_output(Vds, Vgs, heating=True, vsat=True, ambient_temperature=Value(t, ureg.kelvin))
            idrift = [i[0] for k, i in idrift.items() if 'Id' in k]
            idrift = [i if i > 0 else Value(0, i.unit) for i in idrift]
            #
            vg_array = np.arange(0.0, 1.0, 0.025)
            vd_array = np.arange(0.5, 1.0, 0.5)
            idiff = []
            for Vgs in vg_array:
                for Vds in vd_array:
                    idiff.append(S2DModel.compute_diffusion_current(t, Vgs, Vds))


            id = [i + d for i, d in zip(idrift, idiff)]
            plot_idvg_data(vg_array, vd_array, id, 'T = {0}'.format(t))

        #plot_idvg_data(vg_array, vd_array, id, 'With Diffusion Current + $C_Q$')

        # plot_idvg_data(vg_array, vd_array, idrift, 'Only Drift Current')

        I_units = '\u03BCA/\u03BCm'
        plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        plt.ylabel('$I_D$ ({0})'.format(I_units), fontsize=16)
        plt.title('$MoS_2$ FET Subthreshold Current', fontsize=20)

        plt.legend()
        plt.yscale('log')
        plt.show()

        # I_units = '\u03BCA/\u03BCm'
        # plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
        # plt.rc('ytick', labelsize=12)
        # for vds in vd_array:
        #     plt.plot(vg_array, [i * 1e6 for i in id],
        #              label='Vds = {0} V'.format(math.floor(vds * 10) / 10), linewidth=4)
        # # plt.title('$MoS_2$ FET at {0} C'.format(int(ambient_temperature) - 270), fontsize=20)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$I_D$ ({0})'.format(I_units), fontsize=16)

        # plt.legend()
        # plt.yscale('log')
        # plt.show()


def plot_idvg_data(vg_array, vd_array, id, label=None):

    plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=12)
    for vds in vd_array:
        plt.plot(vg_array, [i * 1e6 for i in id],
                 label='Vds = {0} V'.format(math.floor(vds * 10) / 10) if label is None else label,
                 linewidth=4)
    # plt.title('$MoS_2$ FET at {0} C'.format(int(ambient_temperature) - 270), fontsize=20)
    # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
    # plt.ylabel('$I_D$ ({0})'.format(I_units), fontsize=16)
    # plt.legend()
    # plt.yscale('log')
    # plt.show()

