#
# from scipy.integrate import quad
#
# def integrand(x):
#     return x**2
#
# ans, err = quad(integrand, 0, 1)
# print (ans)
#

"""
This module contains code for modeling 2D Schottky FETs.  This is adapted from ''
"""
import scipy

from SemiPy.Physics.DevicePhysics import characteristic_length
from SemiPy.Physics.Modeling.BaseModel import BaseModel
from SemiPy.Devices.Devices.FET.ThinFilmFET import TFT
import math
from scipy.constants import hbar, e, k, pi, h, electron_mass, physical_constants
from scipy.integrate import quad
import numpy as np
import matplotlib.pyplot as plt

class Schottky2DFET(BaseModel):

   def __init__(self):

       #assert isinstance(FET, TFT), 'This model is only valid for ThinFilm Transistors'
       #Compute characteristic length lambda
       self.lambda_semi = 10 * math.pow(10, -9)
       #use body

       #Fitting Parameters: Flat band voltage, electron & hole Schottky barrier, Fermi level
       self.flat_band = 0.0
       self.phi_e = .7
       self.phi_h = -0.3
       self.fermi_level = 0.0

       #Constants: Hole Effective Mass,Elementary Charge, Boltzman Constant, Planks Constants, Valley degeneracy
       self.h_eff_mass = .15 * scipy.constants.electron_mass
       self.e = scipy.constants.e
       self.k = scipy.constants.physical_constants["Boltzmann constant in eV/K"][0]
       self.h = scipy.constants.physical_constants["Planck constant in eV s"][0]
       self.hbar = scipy.constants.physical_constants["Planck constant over 2 pi in eV s"][0]
       self.gv = 6
       self.pi = scipy.constants.pi

       #User Input beyond FET provided Parameters
       self.temp = 300

   #Compute Valence Band Edge as function of Vgs
   def compute_ev(self, vgs):
       return vgs - self.phi_h




   def integrand(self, ev, vds, E):
       const= (2 * self.e * self.gv) / (self.h * self.pi * self.hbar)
       mv_const = 2 * self.h_eff_mass
       f_const = self.k * self.temp
       self.t_const_s = (2 * math.sqrt(2 * self.h_eff_mass) * self.lambda_semi) / ((3 * self.hbar) * (self.phi_h - ev))
       self.t_const_d = (2 * math.sqrt(2 * self.h_eff_mass) * self.lambda_semi) / ((3 * self.hbar) * (-vds + self.phi_h - ev))
       return const * math.sqrt(mv_const * (ev - E)) * np.exp(self.t_const_s * ((E - self.phi_h) ** 3 / 2)) * np.exp(self.t_const_d * ((E + vds - self.phi_h) ** 3 / 2)) * ((1 + np.exp(E / f_const)) - (1 + np.exp((E - vds) / f_const))) / (1 - (1 - np.exp(self.t_const_s * ((E - self.phi_h) ** 3 / 2))) * (1 - np.exp(self.t_const_d * ((E + vds - self.phi_h) ** 3 / 2))))




    #Generate Plot: takes max/min Vgs and number of points to generate
   def generate_plot(self, vgs_min, vgs_max, num_points, vds):
       n = num_points
       self.vgs_array = np.linspace(vgs_min, vgs_max, n)
       self.ids_array = np.zeros(n)
       self.ev_array = np.zeros(n)
       for i in range (n):
           ev = self.ev_array[i] = self.compute_ev(self.vgs_array[i])
           ans,  err = quad(lambda E: self.integrand(ev, vds, E), -math.inf, ev)
           self.ids_array[i] = ans
       self.data_dict = {"vgs": self.vgs_array, "Ev": self.ev_array, "vds =" + str(vds): self.ids_array}
       plt.plot(self.vgs_array, self.data_dict["vds =" + str(vds)])
       plt.show()




self.FET.width/()

model = Schottky2DFET()
model.generate_plot(-1, 0, 50, -.05)
print(model.data_dict)



# print("hole mass is ", scipy.constants.electron_mass)
# print("effective mass is ", model.h_eff_mass)
# print("h is ", model.h)
# print("hbar is ", model.hbar)
# print ("k is ", model.k)



#NEXT STEPS
#