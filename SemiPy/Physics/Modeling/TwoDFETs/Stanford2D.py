"""
This module contains code for modeling 2D Schottky FETs.  This is adapted from ''
"""
from SemiPy.Devices.Devices.FET.ThinFilmFET import TFT
from SemiPy.Physics.Modeling.BaseModel import BaseModel, ModelInput
from SemiPy.Physics.DevicePhysics import compute_sheet_resistance
import math
#from scipy.constants import hbar, electron_mass
from SemiPy.Documentation.Papers.TwoDPapers.TwoDFETPapers import Stanford2DSPaper
from SemiPy.Documentation.ScientificPaper import citation_decorator
from physics.value import Value, ureg
from physics.fundamental_constants import free_space_permittivity_F_div_cm
from physics.fundamental_constants import electron_charge_C
import matplotlib.pyplot as plt
from SemiPy.Devices.Interfaces.Interface import import_interface
from SemiPy.Datasets.IVDataset import IdVdDataSet
import scipy.constants
from dash_cjm.plots.Basic import BasicPlot

import numpy as np

from math import pi, log, tanh


@citation_decorator(Stanford2DSPaper)
class Stanford2DSModel(BaseModel):
    """
    Compact model for modeling traps, parasitic capacitances, velocity saturation, self-heating, and field effects of 2D FETs. The
    reference paper is <citation>, which gives full physical details on the model.
    """

    # Rtbr = Value(1e-7, ureg.meters**2*ureg.kelvin/(ureg.watt))

    # ksub = Value(150, ureg.watt/(ureg.kelvin*ureg.meter))

    eta = 5
    hwop = Value(35e-3, ureg.eV)
    k = Value(scipy.constants.physical_constants["Boltzmann constant in eV/K"][0], ureg.eV/ureg.kelvin)
    k_J = Value(scipy.constants.physical_constants["Boltzmann constant"][0], ureg.J/ ureg.kelvin)
    hcross = Value(scipy.constants.physical_constants["reduced Planck constant"][0], ureg.J * ureg.seconds)
    q = Value(scipy.constants.physical_constants["elementary charge"][0] , ureg.coulombs)

    #Constants for Quantum Capacitance Calculation that need to be defined
    WFTG = Value(4.3,ureg.volt) #Top Gate Work Function [V]
    WFBG = Value(4.3,ureg.volt) #Bottom Gate Work Function [V]
    VFBT = Value(0.305, ureg.volt) #Top Gate Cutoff voltage[V]
    VFBB = Value(0.305, ureg.volt)  #Bottom Gate Cutoff voltage[V]

    # WFTG = 4.3
    # WFBG = 4.3
    # VFBT = 0.305
    # VFBB =0.305


    def __init__(self, FET, *args, **kwargs):

        super(Stanford2DSModel, self).__init__(*args, **kwargs)

        assert isinstance(FET, TFT), 'The Stanford 2DS Model only works with Thin Film transistors.  Yours is {0}'.format(type(FET))

        self.FET = FET

        # get the gate_oxide-channel interface
        self.gate_oxide_channel_interface = import_interface(self.FET.gate_oxide, self.FET.channel)

        self.Rtbr = 1 / self.gate_oxide_channel_interface.thermal_boundary_conductance

        self.thermal_conductance = self.compute_device_thermal_conductance()

        self.thermal_healing_length = self.compute_thermal_healing_length()

        self.vO = self.compute_v0()


    def compute_metal_thermal_resistance(self):
        #using 1 for now to account for the contact resistance
        km = Value(1, ureg.watt / (ureg.meter * ureg.kelvin))
        tm = Value(50, ureg.nanometer)
        Lhm = (tm * self.FET.gate_oxide.thickness * km / self.FET.gate_oxide.thermal_conductivity)**.5

        return Lhm / (km * tm * (self.FET.width.base_units() + 2 * Lhm))

    def compute_thermal_healing_length(self):

        lh = (self.FET.channel.thermal_conductivity*self.FET.channel.thickness*
              (self.FET.width/self.thermal_conductance + self.Rtbr))**0.5
        lh_compact = lh.compact_units()
        return lh.compact_units()


        # return Value(100, ureg.nanometers)

    def compute_power(self, Vds, previous_Id):
        Vds = self.compute_vds_rc(Vds, previous_Id)

        return previous_Id * Vds

    def compute_device_thermal_conductance(self):
        weff = self.FET.width + 2 * self.FET.gate_oxide.thickness

        # computing the inverse of the thermal conductance
        inv_g_1 = self.Rtbr/self.FET.width.base_units()
        inv_g_2 = ((pi * self.FET.gate_oxide.thermal_conductivity)
                   /log(6*(self.FET.gate_oxide.thickness.base_units()/self.FET.width.base_units() + 1))
                   + self.FET.gate_oxide.thermal_conductivity * self.FET.width.base_units() / self.FET.gate_oxide.thickness.base_units())**-1
        inv_g_3 = (1/(self.FET.substrate.thermal_conductivity * 2)*(self.FET.length/weff)**0.5)

        g = (inv_g_1 + inv_g_2 + inv_g_3)**(-1)

        return g

    def compute_vds_rc(self, Vds, previous_Id):
        if self.FET.Rc is not None:
            Vds = Vds - 2 * previous_Id * self.FET.Rc / self.FET.width

        return Vds

    def compute_channel_resistance(self, n, mobility):
        rsh = compute_sheet_resistance(n, mobility)
        rch = rsh * self.FET.length
        return rch

    def compute_drift_current(self, Vds, mobility, Vgs, previous_Id):

        # Vds = self.compute_vds_rc(Vds, previous_Id)
        n = self.FET.vg_to_n(Vgs)
        rch = self.compute_channel_resistance(n, mobility)

        Vds = Vds * rch / (rch + 2 * self.FET.Rc)

        return electron_charge_C * n * mobility * (Vds / self.FET.length) * self.FET.width

    def compute_mobility_temperature(self, ambient_mobility, ambient_temperature, temperature):
        return ambient_mobility * (temperature / ambient_temperature) ** (self.FET.mobility_temperature_exponent * -1)

    def compute_v0(self):
        Nop = self.compute_nop(Value(295, ureg.kelvin))
        # Nop = 1 / (math.exp(self.hwop / (self.k * Value(295, ureg.kelvin))))
        return self.FET.channel.saturation_velocity * (Nop + 1)

    def compute_nop(self, temp):
        return 1 / (math.exp(self.hwop / (self.k * temp)) - 1)

    def compute_saturation_velocity(self, Temp):
        Nop = self.compute_nop(Temp)
        return self.vO / (Nop + 1)

    def compute_mobility_velocity_saturation(self, effective_mobility, Vds, Temp):
        #return effective_mobility
        field = Vds / self.FET.length.adjust_unit(ureg.centimeter)
        vsat = self.compute_saturation_velocity(Temp)
        #return effective_mobility / (1 + (effective_mobility * field / self.FET.channel.saturation_velocity)**self.eta)**(1/self.eta)
        return effective_mobility / (1 + (effective_mobility * field / vsat)**self.eta)**(1/self.eta), vsat

    def compute_temperature(self, power, ambient_temperature, metal_thermal_resistance=None):
        if metal_thermal_resistance is None:
            #metal_thermal_resistance = Value(0.0, unit=ureg.kelvin / ureg.watt)

            metal_thermal_resistance = self.compute_metal_thermal_resistance()

        x = tanh(self.FET.length.base_units() / (2 * self.thermal_healing_length.base_units()))

        t_part = self.thermal_conductance * self.thermal_healing_length.base_units() * metal_thermal_resistance * x

        t_1 = (1 + t_part - 2 * x * self.thermal_healing_length.base_units() / self.FET.length.base_units()) / (1 + t_part)

        average_temperature = ambient_temperature + power * (1 / (self.thermal_conductance * self.FET.length.base_units())) * t_1

        return average_temperature

    def compute_quantum_cap(self, ambient_temperature, Vgs):

        T = Value(ambient_temperature, ureg.kelvin)
        # Material Parameters
        self.g = 2  # Spin Degenracy
        self.gv1 = 1;  # Degenracy of first valley
        self.gv2 = 1;  # Degeneracy of second valley
        self.me1_eff = Value(0.45 * scipy.constants.electron_mass, ureg.kilograms)  # Effective mass of first valley
        self.me2_eff = Value(0.45 * scipy.constants.electron_mass, ureg.kilograms)   # Effective mass of second valley
        self.vth = self.k_J * T / self.q
        self.delEC = 3 * self.vth  # Energy difference from the first valley(Set high to ignore this valley in charge calculations)
        self.epsilon_channel = self.FET.channel.relative_permittivity * free_space_permittivity_F_div_cm
        self.d = self.FET.channel.thickness.base_units() #channel thickness

        self.epsilon_ox = self.FET.gate_oxide.relative_permittivity * free_space_permittivity_F_div_cm
        self.EOT = self.FET.gate_oxide.thickness
        #self.epsilon_ox_b =
        #self.EOTB =
        self.cox_t = (self.epsilon_ox / self.EOT).adjust_unit(ureg.coulombs / (ureg.volts * ureg.meter ** 2))
        self.cox_b = (self.epsilon_ox / self.EOT).adjust_unit(ureg.coulombs / (ureg.volts * ureg.meter ** 2))
        #Using Values From Matlab
        #self.cox_t = Value((20 * 8.854 * 1e-12) / (3e-9), ureg.coulombs / (ureg.volts * ureg.meter ** 2))
        #self.cox_b = Value((1 * 8.854 * 1e-12) / (200e-9), ureg.coulombs / (ureg.volts * ureg.meter ** 2))

        #Calculate electrostatic screening lengths
        self.lambdaT = (self.epsilon_channel * self.d / self.cox_t) ** (1/2)
        self.lambdaB = (self.epsilon_channel * self.d/ self.cox_b) ** (1/2)
        self.A = (self.lambdaT ** (-2) + self.lambdaB ** (-2)) ** (1/2)

        # Calculate Effective density of states for each valley
        self.NDOS1 = (self.gv1 * self.me1_eff * self.k_J * T) / (pi * self.hcross ** 2)
        self.NDOS2 = (self.gv2 * self.me2_eff * self.k_J * T) / (pi * self.hcross ** 2)
        self.NDOS = self.NDOS2
        self.alpha = self.NDOS1 / self.NDOS
        self.beta = self.NDOS2 / self.NDOS
        self.Nimp = Value( 3.5e11 ,ureg.meters ** -2)

        VDS = Value(0.0, ureg.volts)
        VS = Value(0.0, ureg.volts)
        VD = VS + VDS
        VG = [Vgs, Vgs+.01]
        xg_length = len(VG)

        array_size = 10000

        self.phi = np.zeros(array_size)
        self.f = np.zeros(array_size)
        self.fd = np.zeros(array_size)
        self.phis = np.zeros(array_size)
        self.n2d = np.zeros(len(VG))
        self.Es = np.zeros(len(VG))
        self.Eox = np.zeros(len(VG))
        self.Cg = np.zeros(len(VG))
        self.Cq = np.zeros(len(VG))

        for j in range(xg_length):
            VG_units = Value(VG[j], ureg.volts)
            VBG = VG_units
            B = ((VG_units - self.VFBT) / (self.lambdaT ** 2)) + ((VBG - self.VFBB) / (self.lambdaB ** 2))
            i = 1
            self.phi[i] = VG_units
            self.p = Value(self.phi[i], ureg.volts)

            self.f[i] = (1 + math.exp((self.p - VS) / self.vth)) ** self.alpha * (1 + math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta - math.exp(
                  (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p) + (self.Nimp / self.NDOS))


            self.fd[i] = (1 + math.exp((self.p - VS) / self.vth)) ** self.alpha * (1 + math.exp((self.p- VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta * (((self.beta * math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)) / (self.vth * (1 + math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)))) + ((self.alpha * math.exp((self.p - VS) / self.vth)) / (self.vth * (1 + math.exp((self.p - VS) / self.vth))))) + ((self.A ** 2) * (self.epsilon_channel * self.d / (self.q * self.NDOS))) * math.exp((self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p) + (self.Nimp / self.NDOS))

            iter = 0
            while (abs(self.f[i]) > 1e-06) : #termination condition
                iter = iter + 1
                self.phi[i + 1] = (self.phi[i] - (self.f[i]) / (self.fd[i]))
                self.p_1 = Value(self.phi[i + 1], ureg.volts)
                self.f[i + 1] = (1 + math.exp((self.p_1 - VS) / self.vth)) ** self.alpha * (
                            1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta - math.exp(
                    (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p_1) + (self.Nimp / self.NDOS))

                self.fd[i + 1] = (1 + math.exp((self.p_1 - VS) / self.vth)) ** self.alpha * (
                            1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta * (((self.beta * math.exp(
                    (self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)) / (self.vth * (
                            1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)))) + ((self.alpha * math.exp(
                    (self.p_1 - VS) / self.vth)) / (self.vth * (1 + math.exp((self.p_1 - VS) / self.vth))))) + (
                                        (self.A ** 2) * (self.epsilon_channel * self.d / (self.q * self.NDOS))) * math.exp(
                    (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p_1) + (self.Nimp / self.NDOS))
                i = i + 1

            self.phis[j] = self.phi[i]
            self.ph = Value(self.phis[j], ureg.volts)
            #Charge density in the 2D layer(m ^ -2)
            self.n2d[j] = (self.epsilon_channel * self.d / self.q) * (B - (self.A ** 2) * self.ph) + self.Nimp
            #Electic field at the surface (V/m)
            self.Es[j] = self.q * self.n2d[j] / self.epsilon_channel
            #Electric field in the oxide
            self.Eox[j] = (self.epsilon_ox / self.epsilon_channel) * ((VG[j] - self.VFBT - self.phis[j]) / self.EOT)

        self.n2d = np.trim_zeros(self.n2d, 'b')
        self.phis = np.trim_zeros(self.phis, 'b')
        
        #Capacitance Calculation
        Cg = np.divide (np.diff(self.q * self.n2d * 1e-4), np.diff(VG))
        CQ = np.divide (np.diff(self.q * self.n2d * 1e-4), np.diff(self.phis))

        #Plot Channel Voltage vs Vgs
        # plt.plot(VG, self.phis)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$V_C$$_H$ ', fontsize=16)
        # plt.show()
        #
        # #Plot Carrier Concentration vs Vgs
        # plt.plot(VG, self.n2d)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$n_2$$_D$ ', fontsize=16)
        # plt.show()
        #
        # # Log plot Gate Capacitance vs Vgs
        # plt.semilogy(VG[1:], Cg)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$C_g$ ', fontsize=16)
        # plt.show()

        # Log plot Gate Capacitance vs Vgs
        # plt.semilogy(VG[1:], CQ)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$C_q$ ', fontsize=16)
        # #plt.show()
        print("Vgs is ", VG)
        print("CQ is ", CQ)

    def compute_quantum_cap(self, ambient_temperature, Vgs):

        T = Value(ambient_temperature, ureg.kelvin)
        # Material Parameters
        self.g = 2  # Spin Degenracy
        self.gv1 = 1  # Degenracy of first valley
        self.gv2 = 1  # Degeneracy of second valley
        self.me1_eff = Value(0.45 * scipy.constants.electron_mass, ureg.kilograms)  # Effective mass of first valley
        self.me2_eff = Value(0.45 * scipy.constants.electron_mass,
                             ureg.kilograms)  # Effective mass of second valley
        self.vth = self.k_J * T / self.q
        self.delEC = 3 * self.vth  # Energy difference from the first valley(Set high to ignore this valley in charge calculations)
        self.epsilon_channel = self.FET.channel.relative_permittivity * free_space_permittivity_F_div_cm
        self.d = self.FET.channel.thickness.base_units()  # channel thickness

        self.epsilon_ox = self.FET.gate_oxide.relative_permittivity * free_space_permittivity_F_div_cm
        self.EOT = self.FET.gate_oxide.thickness
        # self.epsilon_ox_b =
        # self.EOTB =
        self.cox_t = (self.epsilon_ox / self.EOT).adjust_unit(ureg.coulombs / (ureg.volts * ureg.meter ** 2))
        self.cox_b = (self.epsilon_ox / self.EOT).adjust_unit(ureg.coulombs / (ureg.volts * ureg.meter ** 2))

        # Calculate electrostatic screening lengths
        self.lambdaT = (self.epsilon_channel * self.d / self.cox_t) ** (1 / 2)
        self.lambdaB = (self.epsilon_channel * self.d / self.cox_b) ** (1 / 2)
        self.A = (self.lambdaT ** (-2) + self.lambdaB ** (-2)) ** (1 / 2)

        # Calculate Effective density of states for each valley
        self.NDOS1 = (self.gv1 * self.me1_eff * self.k_J * T) / (pi * self.hcross ** 2)
        self.NDOS2 = (self.gv2 * self.me2_eff * self.k_J * T) / (pi * self.hcross ** 2)
        self.NDOS = self.NDOS2
        self.alpha = self.NDOS1 / self.NDOS
        self.beta = self.NDOS2 / self.NDOS
        self.Nimp = Value(3.5e11, ureg.meters ** -2)

        VDS = Value(0.0, ureg.volts)
        VS = Value(0.0, ureg.volts)
        VD = VS + VDS
        VG = [Vgs, Vgs + .01]
        xg_length = len(VG)

        array_size = 10000

        self.phi = np.zeros(array_size)
        self.f = np.zeros(array_size)
        self.fd = np.zeros(array_size)
        self.phis = np.zeros(array_size)
        self.n2d = np.zeros(len(VG))
        self.Es = np.zeros(len(VG))
        self.Eox = np.zeros(len(VG))
        self.Cg = np.zeros(len(VG))
        self.Cq = np.zeros(len(VG))

        for j in range(xg_length):
            VG_units = Value(VG[j], ureg.volts)
            VBG = VG_units
            B = ((VG_units - self.VFBT) / (self.lambdaT ** 2)) + ((VBG - self.VFBB) / (self.lambdaB ** 2))
            i = 1
            self.phi[i] = VG_units
            self.p = Value(self.phi[i], ureg.volts)

            self.f[i] = (1 + math.exp((self.p - VS) / self.vth)) ** self.alpha * (1 + math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta - math.exp(
                (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p) + (self.Nimp / self.NDOS))

            self.fd[i] = (1 + math.exp((self.p - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta * (((self.beta * math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)) / (self.vth * (
                                       1 + math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)))) + ((self.alpha * math.exp((self.p - VS) / self.vth)) / (
                                   self.vth * (1 + math.exp((self.p - VS) / self.vth))))) + ((self.A ** 2) * (self.epsilon_channel * self.d / (self.q * self.NDOS))) * math.exp((self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p) + (self.Nimp / self.NDOS))

            iter = 0
            while (abs(self.f[i]) > 1e-06):  # termination condition
                iter = iter + 1
                self.phi[i + 1] = (self.phi[i] - (self.f[i]) / (self.fd[i]))
                self.p_1 = Value(self.phi[i + 1], ureg.volts)
                self.f[i + 1] = (1 + math.exp((self.p_1 - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(
                    -self.delEC / self.vth)) ** self.beta - math.exp(
                    (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p_1) + (
                                self.Nimp / self.NDOS))

                self.fd[i + 1] = (1 + math.exp((self.p_1 - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(
                    -self.delEC / self.vth)) ** self.beta * (((self.beta * math.exp(
                    (self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)) / (self.vth * (
                        1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)))) + (
                                                                         (self.alpha * math.exp(
                                                                             (self.p_1 - VS) / self.vth)) / (
                                                                                     self.vth * (1 + math.exp(
                                                                                 (self.p_1 - VS) / self.vth))))) + (
                                         (self.A ** 2) * (
                                             self.epsilon_channel * self.d / (self.q * self.NDOS))) * math.exp(
                    (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p_1) + (
                                self.Nimp / self.NDOS))
                i = i + 1

            self.phis[j] = self.phi[i]
            self.ph = Value(self.phis[j], ureg.volts)
            # Charge density in the 2D layer(m ^ -2)
            self.n2d[j] = (self.epsilon_channel * self.d / self.q) * (B - (self.A ** 2) * self.ph) + self.Nimp
            # Electic field at the surface (V/m)
            self.Es[j] = self.q * self.n2d[j] / self.epsilon_channel
            # Electric field in the oxide
            self.Eox[j] = (self.epsilon_ox / self.epsilon_channel) * ((VG[j] - self.VFBT - self.phis[j]) / self.EOT)

        self.n2d = np.trim_zeros(self.n2d, 'b')
        self.phis = np.trim_zeros(self.phis, 'b')

        # Capacitance Calculation
        Cg = Value( np.diff(self.q * self.n2d * 1e-4) / np.diff(VG)[0],  ureg.coulomb / ureg.meter ** 2 / ureg.volt)
        CQ = Value( np.diff(self.q * self.n2d * 1e-4) / np.diff(self.phis)[0], ureg.coulomb / ureg.meter ** 2 / ureg.volt )

        print("Vgs is ", VG)
        print("CQ is ", CQ)

        return CQ

    def compute_quantum_cap_array(self, ambient_temperature, Vgs_array):

        T = Value(ambient_temperature, ureg.kelvin)
        VDS = Value(0.0, ureg.volts)
        VS = Value(0.0, ureg.volts)
        VD = VS + VDS
        VG = Vgs_array
        xg_length = len(VG)

        array_size = 10000

        self.phi = np.zeros(array_size)
        self.f = np.zeros(array_size)
        self.fd = np.zeros(array_size)
        self.phis = np.zeros(array_size)
        self.n2d = np.zeros(len(VG))
        self.Es = np.zeros(len(VG))
        self.Eox = np.zeros(len(VG))
        self.Cg = np.zeros(len(VG))
        self.Cq = np.zeros(len(VG))

        for j in range(xg_length):
            VG_units = Value(VG[j], ureg.volts)
            VBG = VG_units
            B = ((VG_units - self.VFBT) / (self.lambdaT ** 2)) + ((VBG - self.VFBB) / (self.lambdaB ** 2))
            i = 1
            self.phi[i] = VG_units
            self.p = Value(self.phi[i], ureg.volts)

            self.f[i] = (1 + math.exp((self.p - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p - VS) / self.vth) * math.exp(
                    -self.delEC / self.vth)) ** self.beta - math.exp(
                (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p) + (
                            self.Nimp / self.NDOS))

            self.fd[i] = (1 + math.exp((self.p - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p - VS) / self.vth) * math.exp(-self.delEC / self.vth)) ** self.beta * ((
                                                                                                                               (
                                                                                                                                           self.beta * math.exp(
                                                                                                                                       (
                                                                                                                                                   self.p - VS) / self.vth) * math.exp(
                                                                                                                                       -self.delEC / self.vth)) / (
                                                                                                                                           self.vth * (
                                                                                                                                               1 + math.exp(
                                                                                                                                           (
                                                                                                                                                       self.p - VS) / self.vth) * math.exp(
                                                                                                                                           -self.delEC / self.vth)))) + (
                                                                                                                               (
                                                                                                                                           self.alpha * math.exp(
                                                                                                                                       (
                                                                                                                                                   self.p - VS) / self.vth)) / (
                                                                                                                                           self.vth * (
                                                                                                                                               1 + math.exp(
                                                                                                                                           (
                                                                                                                                                       self.p - VS) / self.vth))))) + (
                                     (self.A ** 2) * (
                                         self.epsilon_channel * self.d / (self.q * self.NDOS))) * math.exp(
                (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p) + (
                            self.Nimp / self.NDOS))

            iter = 0
            while (abs(self.f[i]) > 1e-06):  # termination condition
                iter = iter + 1
                self.phi[i + 1] = (self.phi[i] - (self.f[i]) / (self.fd[i]))
                self.p_1 = Value(self.phi[i + 1], ureg.volts)
                self.f[i + 1] = (1 + math.exp((self.p_1 - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(
                    -self.delEC / self.vth)) ** self.beta - math.exp(
                    (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p_1) + (
                                self.Nimp / self.NDOS))

                self.fd[i + 1] = (1 + math.exp((self.p_1 - VS) / self.vth)) ** self.alpha * (
                        1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(
                    -self.delEC / self.vth)) ** self.beta * (((self.beta * math.exp(
                    (self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)) / (self.vth * (
                        1 + math.exp((self.p_1 - VS) / self.vth) * math.exp(-self.delEC / self.vth)))) + (
                                                                         (self.alpha * math.exp(
                                                                             (self.p_1 - VS) / self.vth)) / (
                                                                                     self.vth * (1 + math.exp(
                                                                                 (self.p_1 - VS) / self.vth))))) + (
                                         (self.A ** 2) * (
                                             self.epsilon_channel * self.d / (self.q * self.NDOS))) * math.exp(
                    (self.epsilon_channel * self.d / (self.q * self.NDOS)) * (B - (self.A ** 2) * self.p_1) + (
                                self.Nimp / self.NDOS))
                i = i + 1

            self.phis[j] = self.phi[i]
            self.ph = Value(self.phis[j], ureg.volts)
            # Charge density in the 2D layer(m ^ -2)
            self.n2d[j] = (self.epsilon_channel * self.d / self.q) * (B - (self.A ** 2) * self.ph) + self.Nimp
            # Electic field at the surface (V/m)
            self.Es[j] = self.q * self.n2d[j] / self.epsilon_channel
            # Electric field in the oxide
            self.Eox[j] = (self.epsilon_ox / self.epsilon_channel) * ((VG[j] - self.VFBT - self.phis[j]) / self.EOT)

        self.n2d = np.trim_zeros(self.n2d, 'b')
        self.phis = np.trim_zeros(self.phis, 'b')

        # Capacitance Calculation
        Cg = np.divide(np.diff(self.q * self.n2d * 1e-4), np.diff(VG))
        CQ = np.divide(np.diff(self.q * self.n2d * 1e-4), np.diff(self.phis))


        # Plot Channel Voltage vs Vgs
        # plt.plot(VG, self.phis)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$V_C$$_H$ ', fontsize=16)
        # plt.show()
        #
        # #Plot Carrier Concentration vs Vgs
        # plt.plot(VG, self.n2d)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$n_2$$_D$ ', fontsize=16)
        # plt.show()
        #
        # # Log plot Gate Capacitance vs Vgs
        # plt.semilogy(VG[1:], Cg)
        # plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        # plt.ylabel('$C_g$ ', fontsize=16)
        # plt.show()

        #Log plot Quantum Capacitance vs Vgs
        plt.semilogy(VG[1:], CQ)
        plt.xlabel('$V_G$$_S$ (V)', fontsize=16)
        plt.ylabel('$C_q$ ', fontsize=16)
        plt.show()
        print("Vgs is ", VG)
        print("CQ is ", CQ)


    def compute_diffusion_current(self, ambient_temp, vgs, vd):
        #Capacitance Values
        self.c_Q = self.compute_quantum_cap(ambient_temp, vgs)
        self.c_i = self.cox_t
        self.c_it = self.q * Value(1e15, ureg.meter ** -2 / ureg.volt)
        self.cap_r = 1 + (self.c_Q + self.c_it) / self.c_i

        #Mobility
        mobility_temp = Value(295, ureg.kelvin)
        T = Value(ambient_temp, ureg.kelvin)
        mobility = self.compute_mobility_temperature(self.FET.max_mobility, mobility_temp, T).adjust_unit(ureg.meter ** 2 / ureg.second / ureg.volt)

        #Compute Diffusion Current
        self.i_diff = (mobility * (self.c_Q + self.c_it) * (self.FET.width / self.FET.length) * (self.vth ** 2) * (1-math.exp(-vd/self.vth)) * math.exp((vgs-self.FET.Vt_avg)/(self.vth * self.cap_r))).adjust_unit(ureg.ampere)
        print("Diffusion Current is ", self.i_diff)

        return self.i_diff

    def plot_diffusion_current(self, ambient_temp, vgs_array, vd_array):
        idiff_vgs_dict = {"vgs": vgs_array}
        length = len(vgs_array)

        for d in vd_array:
            i_diff = []
            cq = []
            for i in range(length):
                i_diff.append(self.compute_diffusion_current(ambient_temp, vgs_array[i], d))
                cq.append(self.Cq)
            idiff_vgs_dict["vds = " + str(d)] = np.array(i_diff)
            idiff_vgs_dict["cq = " + str(d)] = np.array(cq)

        plt.plot(vgs_array, idiff_vgs_dict["vds = " + str(vd_array[1])])
        plt.yscale('log')
        plt.show()

        plt.plot(vgs_array, idiff_vgs_dict["cq = " + str(vd_array[1])])
        plt.yscale('log')
        plt.show()


        #def model_output(self, Vds, Vgs, ambient_temperature=None):
    def model_output(self, Vds, Vgs, heating=True, vsat=True, ambient_temperature=None, iterations=2, linestyle='-'):
        mobility_temp = Value(295, ureg.kelvin)
        if ambient_temperature is None:
            ambient_temperature = Value(295, ureg.kelvin)
        colors = ['C0', 'C2', 'C3']
        assert isinstance(Vds, ModelInput)
        assert isinstance(Vgs, ModelInput)

        # first calculate an initial Id value assuming room temperature (at low Vds this is a good assumption)
        # make sure the starting field is less than 0.25 V / um
        # if Vds.range[0] == 0.0:
        #     Vds.range[0] = Vds.range[1]
        # make sure the Vgs is above threshold
        assert Vgs.range[0] > self.FET.Vt_avg, 'The Vgs values should be above the average threshold voltage {0},' \
                                               ' your min is {1}'.format(self.FET.Vt_avg, Vgs.range[0])
        assert Vds.range[0] / self.FET.length <= Value(0.25, ureg.volt / ureg.micrometer),\
            'Your starting field should be less than 0.25 V /um, yours is {0}'.format(Vds.range[0] / self.FET.length)

        # create a holder for the data
        idvd_data = {}
        for vg in Vgs.range:
            idvd_data['Id_{0}'.format(vg)] = []
            idvd_data['T_{0}'.format(vg)] = []
            idvd_data['Add_{0}'.format(vg)] = []
            idvd_data['vsat_{0}'.format(vg)] = []
        idvd_data['Vds'] = Vds.range

        # now loop through the Vgs values
        for vgs in Vgs.range:
            # first calculate an initial Id
            prev_Id = Value(0.0, ureg.amp)
            # prev_Id = self.compute_drift_current(Vds.range[0], self.FET.max_mobility, Vgs.range[0], prev_Id)

            # now loop through each Vds value
            for vds in Vds.range:
                # for i in range(iterations):
                # vds = self.compute_vds_rc(vds, prev_Id)
                power = self.compute_power(vds, prev_Id)
                # If self heating is turned off, then just use the ambient tempeature
                if not heating:
                    temperature = ambient_temperature
                else:
                    temperature = self.compute_temperature(power, ambient_temperature)

                # compute the new mobility at this temperature
                effective_mobility = self.compute_mobility_temperature(self.FET.max_mobility,
                                                                         mobility_temp,
                                                                         temperature)
                # now compute the mobility at this field

                if vsat:
                    effective_mobility, vsat = self.compute_mobility_velocity_saturation(effective_mobility, vds, temperature)
                    idvd_data['vsat_{0}'.format(vgs)].append(vsat)

                # now calculate the new current
                prev_Id = self.compute_drift_current(vds, effective_mobility, vgs, prev_Id).base_units()

                idvd_data['Id_{0}'.format(vgs)].append(prev_Id / self.FET.width)
                idvd_data['T_{0}'.format(vgs)].append(temperature)
        I_units = '\u03BCA/\u03BCm'
        plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=12)
        for i_vg, vgs in enumerate(Vgs.range):
            plt.plot(idvd_data['Vds'], [i * 1e6 for i in idvd_data['Id_{0}'.format(vgs)]], colors[i_vg] + linestyle,
                     label='Vgs = {0} V'.format(math.floor(vgs * 10) / 10), linewidth=4)
        plt.title('$MoS_2$ FET at {0} C'.format(int(ambient_temperature) - 270), fontsize=20)
        plt.xlabel('$V_D$$_S$ (V)', fontsize=16)
        plt.ylabel('$I_D$ ({0})'.format(I_units), fontsize=16)
        # plt.legend()
        # plt.show()

        # for vgs in Vgs.range:
        #     plt.scatter(idvd_data['Vds'], idvd_data['T_{0}'.format(vgs)],
        #              label='Vgs = {0} V'.format(math.floor(vgs * 10) / 10))
        # plt.title('$MoS_2$ FET at {0} C'.format(int(ambient_temperature) - 270), fontsize=20)
        # plt.xlabel('$V_D$$_S$ (V)', fontsize=16)
        # plt.ylabel('Temperature (K)', fontsize=16)
        # plt.legend()
        # plt.show()
        # plt.savefig('Temp_plot_at_{0}'.format(ambient_temperature))
        # plt.show()

        # for vgs in Vgs.range:
        #     plt.scatter(idvd_data['Vds'], idvd_data['vsat_{0}'.format(vgs)],
        #                 label='Vgs = {0} V'.format(math.floor(vgs * 10) / 10))
        # plt.title('$MoS_2$ FET at {0} C'.format(int(ambient_temperature) - 270), fontsize=20)
        # plt.xlabel('$V_D$$_S$ (V)', fontsize=16)
        # plt.ylabel('vsat (cm/s)', fontsize=16)
        # plt.legend()
        # plt.show()
        # plt.savefig('vsat_plot_at_{0}'.format(ambient_temperature))
        # plt.show()

        idvd_plot = BasicPlot(x_label='VDS (V)', y_label='ID ({0})'.format(I_units), marker_size=8.0)

        for vgs in Vgs.range:
            idvd_plot.add_data(x_data=idvd_data['Vds'], y_data=[i * 1e6 for i in idvd_data['Id_{0}'.format(vgs)]],
                               mode='markers', name='Vgs = {0} V'.format(math.floor(vgs * 10) / 10), text='')

        # idvd_plot.save_plot(name='IdVd_plot_at_{0}'.format(ambient_temperature))

        temp_plot = BasicPlot(x_label='VDS (V)', y_label='Temperature (K)', marker_size=8.0)

        for vgs in Vgs.range:
            temp_plot.add_data(x_data=idvd_data['Vds'], y_data=idvd_data['T_{0}'.format(vgs)], mode='markers',
                               name='Vgs = {0} V'.format(math.floor(vgs * 10) / 10), text='')

        # temp_plot.save_plot(name='Temp_plot_at_{0}'.format(ambient_temperature))


