import numpy as np
from physics.fundamental_constants import free_space_permittivity_F_div_cm, electron_charge_C
from SemiPy.Devices.BaseDevice import BaseDevice
from SemiPy.Devices.FET.TransistorProperties import CurrentDensity, Transconductance, SubthresholdSwing, Voltage
from physics.helper import assert_value
from physics.units import ureg
from physics.value import Value
import csv
from os.path import join


class Transistor(BaseDevice):

    def __init__(self, width, length, *args, **kwargs):
        """

        Args:
            width (physics.Value): The width of the device.
            length (physics.Value): The length of the device.
            *args:
            **kwargs:
        Example::


        """
        super(Transistor, self).__init__(*args, **kwargs)

        assert isinstance(width, Value), 'The width must be of type value.'
        assert isinstance(length, Value), 'The length must of type value.'
        self.width = width
        self.length = length

        # publish properties
        self._add_publish_property('width')
        self._add_publish_property('length')


class FET(Transistor):

    def __init__(self, dielectric_const, tox, *args, **kwargs):
        super(FET, self).__init__(*args, **kwargs)
        # save the FET parameters
        self.dielectric_const = dielectric_const
        self.tox = tox
        self.Cox = (free_space_permittivity_F_div_cm * self.dielectric_const / self.tox).adjust_unit(
            ureg.farad / (ureg.centimeter ** 2))

        # placeholders
        self.max_mobility = None
        self.max_gm = Transconductance()
        # self._max_gm_Vd = None
        self._min_ss = SubthresholdSwing()
        self.Vt_bwd = Voltage()
        self.Vt_fwd = Voltage()
        self.Vt_avg = Voltage()
        self.hysteresis = Voltage()
        self.max_Ion = CurrentDensity()
        # self._max_Ion_Vd = None
        # self._max_Ion_F = None
        # self._max_Ion_Vg = None
        # self._max_Ion_n = None
        # self._Ion_1V_1e13 = None
        # self._Ion_1e13 = None
        # self._Ion_1e13_Vd = None

        # add to the publish properties
        # self._add_publish_property('mobility')
        # self._add_publish_property('dielectric_constant')
        # self._add_publish_property('tox')
        # self._add_publish_property('Cox')
        # self._add_publish_property('max_gm')
        # self._add_publish_property('max_ss')
        # self._add_publish_property('Vt_fwd')
        # self._add_publish_property('Vt_bwd')
        # self._add_publish_property('hysteresis')
        # self._add_publish_property('max_Ion')
        # self._add_publish_property('max_Ion_Vd')
        # self._add_publish_property('max_Ion_Field')
        # self._add_publish_property('max_Ion_Vg')
        # self._add_publish_property('max_Ion_n')

    # def set(self, prop_name, value):

    def compute_properties(self):
        """
        Compute properties of the FET given the available data
        Returns:
            None
        """
        # first hysteresis, then mobility
        if self.Vt_bwd is not None and self.Vt_fwd is not None:
            self.hysteresis.set(self.Vt_fwd.prop_value - self.Vt_bwd.prop_value)
            self.Vt_avg.set((self.Vt_fwd.prop_value + self.Vt_bwd.prop_value) / 2.0)

        if self.Cox is not None and self.max_gm.prop_value is not None and self.length is not None:
            mobility = self.length * self.max_gm.prop_value / (self.Cox * self.max_gm['Vd'])
            mobility = mobility.adjust_unit(ureg.centimeter * ureg.centimeter / (ureg.volt * ureg.second))
            self.max_mobility.set(mobility, {'Vg': self.max_gm['Vg'], 'Vd': self.max_gm['Vd']})

    def norm_Id(self, Id):
        return Id/self.width

    def norm_Field(self, vd):
        return vd/self.width

    # def norm_Vg(self, vg):
    #     return vg

    def vg_to_n(self, vg):
        n = self.Cox * (vg - self.Vt_avg) / electron_charge_C
        return n

    # @property
    # def Vt_fwd(self):
    #     return self._Vt_fwd
    #
    # @Vt_fwd.setter
    # def Vt_fwd(self, _in):
    #     assert_value(_in)
    #     self._Vt_fwd = _in
    #
    # @property
    # def Vt_bwd(self):
    #     return self._Vt_bwd
    #
    # @Vt_bwd.setter
    # def Vt_bwd(self, _in):
    #     assert_value(_in)
    #     self._Vt_bwd = _in

    # @property
    # def mobility(self):
    #     return self._mobility
    #
    # @mobility.setter
    # def mobility(self, _in):
    #     assert_value(_in)
    #     self._mobility = _in

    # @property
    # def max_gm(self):
    #     return self._max_gm
    #
    # @max_gm.setter
    # def max_gm(self, _in):
    #     if isinstance(_in, np.ndarray):
    #         _in = self.max_slope_value(_in)
    #     self._max_gm.set(_in)

    # @property
    # def max_gm_Vd(self):
    #     return self._max_gm_Vd
    #
    # @max_gm_Vd.setter
    # def max_gm_Vd(self, _in):
    #     assert_value(_in)
    #     self._max_gm_Vd = _in

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

    # @property
    # def max_Ion(self):
    #     return self._max_Ion
    #
    # @max_Ion.setter
    # def max_Ion(self, _in):
    #     assert_value(_in)
    #     if _in.unit.dimensionality != ureg.amp/ureg.meter:
    #         _in/self.width
    #     self._max_Ion = _in
    #
    # @property
    # def max_Ion_n(self):
    #     return self._max_Ion_n
    #
    # @max_Ion_n.setter
    # def max_Ion_n(self, _in):
    #     assert_value(_in)
    #     self._max_Ion_n = _in
    #
    # @property
    # def max_Ion_Vd(self):
    #     return self._max_Ion_Vd
    #
    # @max_Ion_Vd.setter
    # def max_Ion_Vd(self, _in):
    #     assert_value(_in)
    #     self.max_Ion_F = self.norm_Field(_in)
    #     self._max_Ion_Vd = _in
    #
    # @property
    # def max_Ion_F(self):
    #     return self._max_Ion_F
    #
    # @max_Ion_F.setter
    # def max_Ion_F(self, _in):
    #     assert_value(_in)
    #     self._max_Ion_F = _in
    #
    # @property
    # def max_Ion_Vg(self):
    #     return self._max_Ion_Vg
    #
    # @max_Ion_Vg.setter
    # def max_Ion_Vg(self, _in):
    #     assert_value(_in)
    #     self.max_Ion_n = self.vg_to_n(_in)
    #     self._max_Ion_Vg = _in

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
        return super(NFET, self).norm_Id(Id)

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
