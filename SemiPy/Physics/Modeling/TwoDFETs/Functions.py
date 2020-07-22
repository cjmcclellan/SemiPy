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
from scipy.constants import hbar, e, k, pi, h, electron_mass
from scipy.integrate import quad
import numpy as np
from physics.value import Value, ureg

class Schottky2DFET(BaseModel):

   def __init__(self):

       #assert isinstance(FET, TFT), 'This model is only valid for ThinFilm Transistors'
       #Compute characteristic length lambda
       self.lambda_semi = Value(value=10, unit=ureg.nanometer)
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
       self.temp = 300

   #Compute Valence Band Edge as function of Vgs
   def compute_ev(self, vgs):
       pass


   #Compute Transmission Probability
   def transmission(self,  hole=False, electron=False):
       pass

   #Compute Fermi Level
   def fermi_level(self, E):
       f_const = self.k * self.temp
       return 1+ math.exp(E/f_const)

   def modes(self, E):
       mv_const = 2 * self.h_eff_mass
       return math.sqrt(mv_const - E)

   def integrate(self):
       ans, err = quad(self.fermi_level, 0, 2)
       return ans
'''
   def integrand(self, ev, vds, E ):
       const= (2 * self.e * self.gv) / (self.h * self.pi * self.hbar)
       mv_const = 2 * self.h_eff_mass * ev
       f_const = self.k * self.temp

       return const * math.sqrt(mv_const - E) * ((1+ math.exp(E/f_const)) - (1+ math.exp((E - self.e*vds)/f_const)))



    #Generate Plot: takes max/min Vgs and number of points to generate
   def generate_plot(self, vgs_min, vgs_max, num_points, vds):
       n = num_points
       self.vgs_array = np.linspace(vgs_min, vgs_max, n)
       self.data_dict = {"vgs": self.vgs_array}
       self.ids_array = np.zeros(n)
       #for i in range (n):
        #   ev = self.compute_ev(self.vgs_array[n])
         #  self.ids_array[i] = quad(self.integrand(ev, vds),-math.inf,ev)
       self.data_dict["vds =" + str(vds)] = self.ids_array
'''


def fermi_level(E, c):
    return (E/c)

def integrate():
    ans, err = quad(lambda E: fermi_level(E, 5), 0, 2)
    return ans

def modes(E):
    return math.sqrt(4 - E)

model = Schottky2DFET()
#model.generate_plot(-1.2, .4, 50, -.005)
#print( model.data_dict["vgs"])
print(integrate())



#NEXT STEPS
#