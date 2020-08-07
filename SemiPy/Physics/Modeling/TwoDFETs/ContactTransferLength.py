"""
This module contains code for modeling 2D Schottky FETs.  This is adapted from ''
"""
from SemiPy.Physics.DevicePhysics import characteristic_length
from SemiPy.Physics.Modeling.BaseModel import BaseModel
import math
from scipy.constants import hbar, electron_mass


class ContactTransferLength(BaseModel):

    def __init__(self, h_mass, e_mass, tox, tchannel, epiox, epichannel, *args, **kwargs):
        super(ContactTransferLength, self).__init__(*args, **kwargs)
        self.h_mass = h_mass * electron_mass
        self.e_mass = e_mass * electron_mass
        self.tox = tox
        self.tchannel = tchannel
        self.epiox = epiox
        self.epichannel = epichannel

        # now compute lambda
        self.lambda_semi = characteristic_length(epichannel=self.epichannel, epiox=self.epiox, tchannel=self.tchannel, tox=self.tox)

        # placeholders for fitting parameters
        self.flat_band = 0.0
        self.phi_e = 0.0
        self.phi_h = 0.0
        self.fermi_level = 0.0

    def __compute_e(self, vgs, phi, x=None, vapp=0.0):
        """
          Ef--|   _______
              |  /
              | /
         phi__|/
        Args:
            vgs:
            phi:
            x:
            vapp:

        Returns:

        """
        E = self.flat_band - phi - vgs
        # if x is none, then get the e in the channel
        if x is None:
            return
        else:
            return -phi

    def __compute_ev(self, vgs):
        return self.flat_band - self.phi_h - vgs

    def transmission(self, E, phib, hole=False, electron=False):
        """
        Compute the transmission
        Args:
            E:

        Returns:

        """
        assert hole or electron, 'You have not selected hole or electron.  You must set one to True.'

        if hole:
            mass = self.h_mass
        else:
            mass = self.e_mass

        # now compute the transmission
        return (2**(5/2) * (mass * (E - phib)) ** (3/2)) / (hbar * 3)

    def __modes(self, E, phib, hole=False, electron=False):
        pass


if __name__ == '__main__':
    model = Schottky2DFET(h_mass=1.0, e_mass=1.0, tox=2, tchannel=2, epiox=3.9, epichannel=4.0)

    model.transmission(E=1.0, phib=3.0)
    a = 5
