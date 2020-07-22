import numpy as np
from physics.fundamental_constants import free_space_permittivity_F_div_cm, electron_charge_C
from SemiPy.Devices.Devices.BaseDevice import BaseDevice, Voltage
from SemiPy.Devices.Devices.FET.TransistorProperties import CurrentDensity, Transconductance, SubthresholdSwing, Mobility
import SemiPy.Devices.Materials.Properties as matprop
from SemiPy.Physics.DevicePhysics import carrier_density
from SemiPy.Devices.PhysicalProperty import CustomPhysicalProperty
# from SemiPy.Devices.Materials.Properties.Interfaces.Electrical import ElectricalContactResistance
# from SemiPy.Devices.Materials.Properties.Interfaces.Thermal import ThermalBoundaryConductance
from SemiPy.Devices.Materials.BaseMaterial import Semiconductor
from physics.helper import assert_value
from physics.units import ureg
from physics.value import Value
import csv
from os.path import join


class Transistor(BaseDevice):
    """

    Args:
        width (physics.Value): The width of the device.
        length (physics.Value): The length of the device.
        *args:
        **kwargs:
    Example::q

    """

    def __init__(self, channel, width, length, *args, **kwargs):

        super(Transistor, self).__init__(*args, **kwargs)

        assert isinstance(width, Value), 'The width must be of type value.'
        assert isinstance(length, Value), 'The length must of type value.'
        self.width = width
        self.length = length

        # publish properties
        self._add_publish_property('width')
        self._add_publish_property('length')

        # save the channel material
        assert isinstance(channel, Semiconductor), 'The channel material must be a semiconductor'
        self.channel = channel


class FET(Transistor):

    mobility_temperature_exponent = CustomPhysicalProperty('mobility_temperature_exponent',
                                                           ureg.dimensionless)

    def __init__(self, gate_oxide, *args, **kwargs):
        """

        Args:
            dielectric_const:
            tox:
            *args:
            **kwargs:
        """
        super(FET, self).__init__(*args, **kwargs)
        # save the FET parameters
        assert isinstance(gate_oxide, Semiconductor), 'The gate oxide must be a semiconductor'
        self.gate_oxide = gate_oxide

        # placeholders
        self.max_mobility = Mobility(name='maximum field-effect mobility')
        self._add_publish_property('max_mobility')
        self.max_gm = Transconductance(name='maximum transconductance')
        self._add_publish_property('max_gm')
        # self._max_gm_Vd = None
        self._min_ss = SubthresholdSwing(name='minimum subthreshold swing')
        # self._add_publish_property('_min_ss')
        self.Vt_bwd = Voltage(name='Backward Sweep Threshold Voltage')
        self.Vt_fwd = Voltage(name='Forward Sweep Threshold Voltage')
        self.Vt_avg = Voltage(name='Average Threshold Voltage')
        self._add_publish_property('Vt_avg')
        self.hysteresis = Voltage(name='Hysteresis')
        self._add_publish_property('hysteresis')
        self.max_Ion = CurrentDensity(name='Maximum Current Density')
        self._add_publish_property('max_Ion')
        # TODO: Vt will depend on Vd.  How should I save that info and adjust for n

        # add some interface properties
        self.Rc = matprop.Interfaces.Electrical.ElectricalContactResistance(name='metal contact resistance')
        self.TBC = matprop.Interfaces.Thermal.ThermalBoundaryConductance(name='gate oxide thermal boundary resistance')

    def compute_properties(self):
        """
        Compute properties of the FET given the available data
        Returns:
            None
        """
        # first hysteresis, then mobility
        if self.Vt_bwd is not None and self.Vt_fwd is not None:
            self.hysteresis.set(self.Vt_fwd.value - self.Vt_bwd.value)
            self.Vt_avg.set((self.Vt_fwd.value + self.Vt_bwd.value) / 2.0)
        elif self.Vt_fwd is not None:
            self.Vt_avg = self.Vt_fwd
        elif self.Vt_bwd is not None:
            self.Vt_avg = self.Vt_bwd

        if self.gate_oxide is not None and self.max_gm.value is not None and self.length is not None:
            mobility = self.length * self.max_gm.value / (self.gate_oxide.capacitance * self.max_gm['Vd'])
            mobility = mobility.adjust_unit(ureg.centimeter * ureg.centimeter / (ureg.volt * ureg.second))
            self.max_mobility.set(mobility, {'Vg': self.max_gm['Vg'], 'Vd': self.max_gm['Vd']})

    def norm_Id(self, Id):
        return Id/self.width

    def norm_Field(self, vd):
        return vd/self.width    # def max_Ion(self):

    def vg_to_n(self, vg):
        # adding extra values to make the units be centimeter ** -2
        # replace any Vg < Vt_avg with Vt_avg
        if isinstance(vg, np.ndarray):
            vg[vg < self.Vt_avg.value] = self.Vt_avg.value
            # n = carrier_density(self.gate_oxide.capacitance, vg, self.Vt_avg.value)
            # n = Value(value=1.0, unit=ureg.coulomb) * self.gate_oxide.capacitance * (vg - self.Vt_avg.value)\
            #     / (electron_charge_C * Value(value=1.0, unit=ureg.volt * ureg.farad))
        try:
            n = Value(value=1.0, unit=ureg.coulomb) * self.gate_oxide.capacitance * (vg - self.Vt_avg.value)\
                / (electron_charge_C * Value(value=1.0, unit=ureg.volt * ureg.farad))

        except Exception as e:
            assert self.Vt_avg.value is not None, \
                'You must calculate the average Vt by running FET.compute_properties() before computing the carrier density'
            raise e
        return n

    @property
    def min_ss(self):
        return self._min_ss

    @min_ss.setter
    def min_ss(self, _in):
        if isinstance(_in, np.ndarray):
            # remove any zeros
            _in = _in.flatten()
            zero_val = Value(0.0, _in[0].unit)
            zero_i = [i for i in range(len(_in)) if _in[i] == zero_val]
            _in = np.delete(_in, zero_i)
            _in = self.min_slope_value(_in)
        _in = _in.adjust_unit(ureg.meter * ureg.millivolt / ureg.amp)
        self._min_ss = _in

    def max_value(self, array, return_index=False):
        raise NotImplementedError('You must implement max_value')

    def min_value(self, array, return_index=False):
        raise NotImplementedError('You must implement max_value')

    def max_slope_value(self, array, return_index=False):
        raise NotImplementedError('You must implement max_value')

    def min_slope_value(self, array, return_index=False):
        raise NotImplementedError('You must implement max_value')

    def _arg_max(self, array):
        # get the arg max of an array
        return np.unravel_index(np.argmax(array), array.shape)

    def _arg_min(self, array):
        # get the arg min of an array
        return np.unravel_index(np.argmin(array), array.shape)


class NFET(FET):

    def __init__(self, *args, **kwargs):
        super(NFET, self).__init__(*args, **kwargs)

    def norm_Id(self, Id):
        # should not have to adjust anything
        return super(NFET, self).norm_Id(Id)   # @property

    def max_value(self, array, return_index=False):
        result = abs(array).max()
        if return_index:
            return result, self._arg_max(abs(array))
        return result

    def min_value(self, array, return_index=False):
        result = abs(array).min()
        if return_index:
            return result, self._arg_min(abs(array))
        return result

    def max_slope_value(self, array, return_index=False):
        return self.max_value(array, return_index)

    def min_slope_value(self, array, return_index=False):
        return self.min_value(array, return_index)


class PFET(FET):

    # TODO: Need to think about adjusting the max Vg and max carrier density functions for PFET vs NFET
    def __init__(self, *args, **kwargs):
        super(PFET, self).__init__(*args, **kwargs)

    def norm_Id(self, Id):
        # should not have to adjust anything
        return super(PFET, self).norm_Id(Id)

    # def norm_Vg(self, vg):
    #     return vg*-1

    def max_value(self, array, return_index=False):
        result = abs(array).max()
        if return_index:
            return result, self._arg_max(abs(array))
        return result

    def min_value(self, array, return_index=False):
        result = abs(array).min()
        if return_index:
            return result, self._arg_min(abs(array))
        return result

    def max_slope_value(self, array, return_index=False):
        array = array * -1
        result = array.max() * -1
        if return_index:
            return result, self._arg_max(array)
        return result

    def min_slope_value(self, array, return_index=False):
        array = array * -1
        result = abs(array).min() * -1
        if return_index:
            return result, self._arg_min(array)
        return result

    def vg_to_n(self, vg):
        # flip the sign of vg
        super(PFET, self).vg_to_n(abs(vg))


class AmbipolarFET(FET):
    """
    An Ambipolar FET is a FET that has both p-type and n-type behavior.  SemiPy represents this as two separate N and P FETs.

    """
    def __init__(self, *args, **kwargs):

        super(AmbipolarFET, self).__init__(*args, **kwargs)

        # create NFET and PFET sub classes
        self._NFET = NFET(*args, **kwargs)
        self._PFET = PFET(*args, **kwargs)

    @property
    def NBranch(self):
        return self._NFET

    @property
    def PBranch(self):
        return self._PFET
