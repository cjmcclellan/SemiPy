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
from SemiPy.Plotting.IVPlotting.IVPlot import IdVgPlot, IdVdPlot
import matplotlib.pyplot as plt
import math

# l = 200
# Vds = 3
#

class Test2DFETModels(unittest.TestCase):

    def test_stanford2dsmodel(self):

        gate_oxide = SiO2(thickness=Value(30.0, ureg.nanometer))
        channel = MoS2(layer_number=1, thickness=Value(0.6, ureg.nanometer))
        # set the channel vsat to 7e6 cm/s
        channel.saturation_velocity.set(Value(3e6, ureg.centimeter / ureg.seconds), input_values={'temperature': Value(300, ureg.kelvin)})
        substrate = Silicon()

        fet = TFT(channel=channel, gate_oxide=gate_oxide, length=Value(400, ureg.nanometer),
                  width=Value(2000, ureg.nanometer), substrate=substrate)

        fet.Vt_avg.set(Value(-10.0, ureg.volt))

        fet.Rc.set(Value(2000.0, ureg.ohm * ureg.micrometer),
                   input_values={'n': Value(1e13, ureg.centimeter**-2)})

        fet.max_mobility.set(Value(30, ureg.centimeter**2 / (ureg.volt * ureg.second)),
                             input_values={'Vd': Value(1, ureg.volt), 'Vg': Value(1, ureg.volt)})

        fet.mobility_temperature_exponent.set(Value(1.15, ureg.dimensionless))

        S2DModel = Stanford2DSModel(FET=fet)

        Vds = ModelInput(0.0, 10.0, num=40, unit=ureg.volt)

        Vgs = ModelInput(-9.0, 30.0, num=5, unit=ureg.volt)

        ambient_temperature = Value(300, ureg.kelvin)


        # plot = IdVdPlot('IdVg')
        fig = plt.figure(dpi=160)
        ax = fig.gca()
        I_units = '\u03BCA/\u03BCm'
        colors = ['C0', 'C2', 'C3', 'C4', 'C5', 'C6']
        linestyle = '-'
        plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=12)
        # ax.axes.get_xaxis().set_ticks([])
        # ax.axes.get_yaxis().set_ticks([])

        # now compute the model output with self-heating
        idvd_data = S2DModel.model_output(Vds, Vgs, heating=True, vsat=True, diffusion=False, drift=True,
                                   ambient_temperature=ambient_temperature)

        for i_vg, vgs in enumerate(Vgs.range):
            plt.plot(idvd_data['Vds'].range, [i * 1e9 for i in idvd_data['Id_{0}'.format(vgs)]], colors[i_vg] + linestyle,
                     label='Vgs = {0} V'.format(math.floor(vgs * 10) / 10), linewidth=4)


        # set the channel vsat to 7e6 cm/s
        fet.channel.saturation_velocity.set(Value(7e6, ureg.centimeter / ureg.seconds), input_values={'temperature': Value(300, ureg.kelvin)})

        S2DModel = Stanford2DSModel(FET=fet)

        # # now compute the model output without self-heating
        idvd_data = S2DModel.model_output(Vds, Vgs, heating=False, vsat=True, diffusion=False, drift=True,
                                          ambient_temperature=ambient_temperature)
        linestyle = '--'
        for i_vg, vgs in enumerate(Vgs.range):
            plt.plot(idvd_data['Vds'].range, [i * 1e9 for i in idvd_data['Id_{0}'.format(vgs)]], colors[i_vg] + linestyle,
                     label='Vgs = {0} V'.format(math.floor(vgs * 10) / 10), linewidth=4)

        # plt.title('$MoS_2$ FET at {0} C'.format(int(ambient_temperature) - 270), fontsize=20)
        # plt.xlabel('$V_D$$_S$ (V)', fontsize=16)
        # plt.ylabel('$I_D$ ({0})'.format(I_units), fontsize=16)
        plt.show()
