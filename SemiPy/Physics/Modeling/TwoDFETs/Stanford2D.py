"""
This module contains code for modeling 2D Schottky FETs.  This is adapted from ''
"""
from SemiPy.Devices.Devices.FET.ThinFilmFET import TFT
from SemiPy.Physics.Modeling.BaseModel import BaseModel, ModelInput
import math
#from scipy.constants import hbar, electron_mass
from SemiPy.Documentation.Papers.TwoDPapers.TwoDFETPapers import Stanford2DSPaper
from SemiPy.Documentation.ScientificPaper import citation_decorator
from physics.value import Value, ureg
from physics.fundamental_constants import electron_charge_C
import matplotlib.pyplot as plt
from SemiPy.Datasets.IVDataset import IdVdDataSet

import numpy as np

from math import pi, log, tanh


@citation_decorator(Stanford2DSPaper)
class Stanford2DSModel(BaseModel):
    """
    Compact model for modeling traps, parasitic capacitances, velocity saturation, self-heating, and field effects of 2D FETs.  The
    reference paper is <citation>, which gives full physical details on the model.
    """

    Rtbr = Value(1e-7, ureg.meters**2*ureg.kelvin/(ureg.watt))

    ksub = Value(150, ureg.watt/(ureg.kelvin*ureg.meter))

    eta = 2

    def __init__(self, FET, *args, **kwargs):

        super(Stanford2DSModel, self).__init__(*args, **kwargs)

        assert isinstance(FET, TFT), 'The Stanford 2DS Model only works with Thin Film transistors.  Yours is {0}'.format(type(FET))

        self.FET = FET

        self.thermal_conductance = self.compute_device_thermal_conductance()

        self.thermal_healing_length = self.compute_thermal_healing_length()

    def compute_thermal_healing_length(self):

        lh = (self.FET.channel.thermal_conductivity.value*self.FET.channel.thickness*
              (self.FET.width/self.thermal_conductance + self.Rtbr))**0.5

        return lh.compact_units()

    def compute_power(self, Vds, previous_Id):
        if self.FET.Rc.value is not None:
            return previous_Id * (Vds - 2 * previous_Id * int(self.FET.Rc.value or 0.0))
        else:
            return previous_Id * Vds

    def compute_device_thermal_conductance(self):
        weff = self.FET.width + 2 * self.FET.gate_oxide.thickness

        # computing the inverse of the thermal conductance
        inv_g_1 = self.Rtbr/self.FET.width.base_units()
        inv_g_2 = ((pi * self.FET.gate_oxide.thermal_conductivity.value)
                   /log(6*(self.FET.gate_oxide.thickness/self.FET.width + 1))
                   + self.FET.gate_oxide.thermal_conductivity.value * self.FET.width / self.FET.gate_oxide.thickness)**-1
        inv_g_3 = (1/(self.ksub * 2)*(self.FET.length/weff)**0.5)

        g = (inv_g_1 + inv_g_2 + inv_g_3)**-1

        return g

    def compute_drift_current(self, Vds, mobility, Vgs):

        return electron_charge_C * self.FET.vg_to_n(Vgs) * mobility * (Vds / self.FET.length) * self.FET.width

    def compute_mobility_temperature(self, ambient_mobility, ambient_temperature, temperature):
        return ambient_mobility / (temperature / ambient_temperature) ** self.FET.mobility_temperature_exponent.value

    def compute_mobility_velocity_saturation(self, effective_mobility, Vds):
        field = Vds / self.FET.length.adjust_unit(ureg.centimeter)
        return effective_mobility / (1 + (effective_mobility * field / self.FET.channel.saturation_velocity.value)**self.eta)**(1/self.eta)

    def compute_temperature(self, power, ambient_temperature, metal_thermal_resistance=None):
        if metal_thermal_resistance is None:
            metal_thermal_resistance = Value(0.0, unit=ureg.kelvin / ureg.watt)

        x = tanh(self.FET.length / (2 * self.thermal_healing_length))

        t_part = self.thermal_conductance * self.thermal_healing_length.base_units() * metal_thermal_resistance * x

        t_1 = (1 + t_part - 2 * x * self.thermal_healing_length / self.FET.length) / (1 + t_part)

        average_temperature = ambient_temperature + power * (1 / (self.thermal_conductance * self.FET.length.base_units())) * t_1

        return average_temperature

    def model_output(self, Vds, Vgs, ambient_temperature=None):

        if ambient_temperature is None:
            ambient_temperature = Value(295, ureg.kelvin)

        assert isinstance(Vds, ModelInput)
        assert isinstance(Vgs, ModelInput)

        # first calculate an initial Id value assuming room temperature (at low Vds this is a good assumption)
        # make sure the starting field is less than 0.25 V / um
        if Vds.range[0] == 0.0:
            Vds.range[0] = Vds.range[1]
        # make sure the Vgs is above threshold
        assert Vgs.range[0] > self.FET.Vt_avg, 'The Vgs values should be above the average threshold voltage {0},' \
                                               ' your min is {1}'.format(self.FET.Vt_avg, Vgs.range[0])
        assert Vds.range[0] / self.FET.length <= Value(0.25, ureg.volt / ureg.micrometer),\
            'Your starting field should be less than 0.25 V /um, yours is {0}'.format(Vds.range[0] / self.FET.length)

        # create a holder for the data
        idvd_data = {'Id_{0}'.format(vg): [] for vg in Vgs.range}
        idvd_data['Vds'] = Vds.range

        # now loop through the Vgs values
        for vgs in Vgs.range:
            # first calculate an initial Id
            prev_Id = self.compute_drift_current(Vds.range[0], self.FET.max_mobility, Vgs.range[0])

            # now loop through each Vds value
            for vds in Vds.range:
                power = self.compute_power(vds, prev_Id)
                temperature = self.compute_temperature(power, ambient_temperature)

                # compute the new mobility at this temperature
                temperature_mobility = self.compute_mobility_temperature(self.FET.max_mobility,
                                                                         ambient_temperature,
                                                                         temperature)
                # now compute the mobility at this field
                effective_mobility = self.compute_mobility_velocity_saturation(temperature_mobility, vds)

                # now calculate the new current
                prev_Id = self.compute_drift_current(vds, effective_mobility, vgs).base_units()

                idvd_data['Id_{0}'.format(vgs)].append(prev_Id)

        for vgs in Vgs.range:
            plt.plot(idvd_data['Vds'], idvd_data['Id_{0}'.format(vgs)])
        plt.show()


