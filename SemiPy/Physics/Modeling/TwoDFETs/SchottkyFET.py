"""
This module contains code for modeling 2D Schottky FETs.  This is adapted from ''
"""
import scipy

from SemiPy.Physics.DevicePhysics import characteristic_length
from SemiPy.Physics.Modeling.BaseModel import BaseModel
from SemiPy.Devices.Devices.FET.ThinFilmFET import TFT
import math
from scipy.constants import hbar, e, k, pi, h, electron_mass,
from scipy.integrate import quad
import numpy as np


class Schottky2DFET(BaseModel):

   def __init__(self, FET, temp):

       assert isinstance(FET, TFT), 'This model is only valid for ThinFilm Transistors'
       #Compute characteristic length lambda
       self.lambda_semi = characteristic_length(epichannel=FET.channel.relative_permittivity,
                                                epiox=FET.gate_oxide.relative_permittivity,
                                                tchannel=FET.channel.thickness,
                                                tox=FET.gate_oxide.thickness)
       #use body

       #Fitting Parameters: Flat band voltage, electron & hole Schottky barrier, Fermi level
       self.flat_band = 0.0
       self.phi_e = .7
       self.phi_h = 0.3
       self.fermi_level = 0.0

       #Constants: Hole Effective Mass,Elementary Charge, Boltzman Constant, Planks Constants, Valley degeneracy
       self.h_eff_mass = .15 * scipy.constants.electron_mass
       self.e = scipy.constants.e
       self.k = scipy.constants.k
       self.h = scipy.constants.h
       self.hbar = scipy.constants.hbar
       self.gv = 6
       self.pi = scipy.constants.pi

       #User Input beyond FET provided Parameters
       self.temp = temp


    #Compute Valence Band Edge as function of Vgs
    def compute_ev(self, vgs):
        return vgs- self.phi_h


    #Compute Transmission Probability
    def transmission(self,  hole=False, electron=False):
        pass

   #Compute Fermi Level
   def fermi_level(self, ):
       pass


   def integrand(self, ev, vds, E ):
       const= (2 * self.e * self.gv) / (self.h * self.pi * self.hbar)
       mv_const = 2 * self.h_eff_mass * ev
       f_const = self.k * self.temp

       return const * math.sqrt(mv_const - E) * ((1+ math.exp(E/f_const)) - (1+ math.exp((E - self.e*vds)/f_const)))

       # Generate Plot: takes max/min Vgs and number of points to generate


   def generate_plot(self, vgs_min, vgs_max, num_points, vds):
       n = num_points
       self.vgs_array = np.linspace(vgs_min, vgs_max, n)
       self.data_dict = {"vgs": self.vgs_array}
       self.ids_array = np.zeros(n)
       # for i in range (n):
       #   ev = self.compute_ev(self.vgs_array[n])
       #  self.ids_array[i] = quad(self.integrand(ev, vds),-math.inf,ev)
       self.data_dict["vds =" + str(vds)] = self.ids_array


model = Schottky2DFET()
model.generate_plot(-1.2, .4, 50, -.005)
print( model.data_dict["vgs"])









#    def __init__(self, h_mass, e_mass, tox, tchannel, epiox, epichannel, *args, **kwargs):
#         super(Schottky2DFET, self).__init__(*args, **kwargs)
#         self.h_mass = h_mass * electron_mass
#         self.e_mass = e_mass * electron_mass
#         self.tox = tox
#         self.tchannel = tchannel
#         self.epiox = epiox
#         self.epichannel = epichannel
#
#         # now compute lambda
#         self.lambda_semi = characteristic_length(epichannel=self.epichannel, epiox=self.epiox, tchannel=self.tchannel, tox=self.tox)
#
#         # placeholders for fitting parameters
#         self.flat_band = 0.0
#         self.phi_e = 0.0
#         self.phi_h = 0.0
#         self.fermi_level = 0.0
#
#     def __compute_e(self, vgs, phi, x=None, vapp=0.0):
#         """
#           Ef--|   _______
#               |  /
#               | /
#          phi__|/
#         Args:
#             vgs:
#             phi:
#             x:
#             vapp:
#
#         Returns:
#
#         """
#         E = self.flat_band - phi - vgs
#         # if x is none, then get the e in the channel
#         if x is None:
#             return
#         else:
#             return -phi
#
#     def __compute_ev(self, vgs):
#         return self.flat_band - self.phi_h - vgs
#
#     def transmission(self, E, phib, hole=False, electron=False):
#         """
#         Compute the transmission
#         Args:
#             E:
#
#         Returns:
#
#         """
#         assert hole or electron, 'You have not selected hole or electron.  You must set one to True.'
#
#         if hole:
#             mass = self.h_mass
#         else:
#             mass = self.e_mass
#
#         # now compute the transmission
#         return (2**(5/2) * (mass * (E - phib)) ** (3/2)) / (hbar * 3)
#
#     def __modes(self, E, phib, hole=False, electron=False):
#         pass
#
#
# if __name__ == '__main__':
#     model = Schottky2DFET(h_mass=1.0, e_mass=1.0, tox=2, tchannel=2, epiox=3.9, epichannel=4.0)
#
#     model.transmission(E=1.0, phib=3.0)
#     a = 5

