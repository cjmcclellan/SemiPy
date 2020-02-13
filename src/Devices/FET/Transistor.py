import numpy as np
from physics.fundamental_constants import free_space_permittivity_F_div_cm, electron_charge_C
from ..BaseDevice import BaseDevice
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
        # self.publish_prop = {'Width': lambda: self.width,
        #                      'length': lambda: self.length}

    # finalize the transistor characteristics into a CSV file
    # def publish_csv(self, path, name):
    #     path = join(path, name + '.csv')
    #     with open(path, 'w') as f:
    #         for key in self.publish_prop.keys():
    #             if isinstance(self.publish_prop[key](), Value):
    #                 f.write("%s,%s,%s\n" % (key, self.publish_prop[key]().value, self.publish_prop[key]().unit))
    #             else:
    #                 f.write("%s,%s\n" % (key, self.publish_prop[key]()))


class FET(Transistor):

    def __init__(self, dielectric_const, tox, *args, **kwargs):
        super(FET, self).__init__(*args, **kwargs)
        # save the FET parameters
        self.dielectric_const = dielectric_const
        self.tox = tox
        self.Cox = (free_space_permittivity_F_div_cm * self.dielectric_const / self.tox).adjust_unit(
            ureg.farad / (ureg.centimeter ** 2))

        # placeholders
        self._mobility = None
        self._max_gm = None
        self._min_ss = None
        self._Vt = None
        self._max_Ion = None
        self._max_Ion_Vd = None
        self._max_Ion_F = None
        self._max_Ion_Vg = None
        self._max_Ion_n = None
        self._Ion_1V_1e13 = None
        self._Ion_1e13 = None
        self._Ion_1e13_Vd = None

        # add to the publish properties
        self._add_publish_property('mobility')
        self._add_publish_property('dielectric_constant')
        self._add_publish_property('tox')
        self._add_publish_property('Cox')
        self._add_publish_property('max_gm')
        self._add_publish_property('max_ss')
        self._add_publish_property('Vt')
        self._add_publish_property('max_Ion')
        self._add_publish_property('max_Ion_Vd')
        self._add_publish_property('max_Ion_Field')
        self._add_publish_property('max_Ion_Vg')
        self._add_publish_property('max_Ion_n')

    def norm_Id(self, Id):
        return Id/self.width

    def norm_Field(self, vd):
        return vd/self.width

    def norm_Vg(self, vg):
        return vg

    def vg_to_n(self, vg):
        n = self.Cox * (vg - self.Vt) / electron_charge_C
        # n[n < Value(0, n[0].unit)] = 0
        return n

    @property
    def Vt(self):
        return self._Vt

    @Vt.setter
    def Vt(self, _in):
        assert_value(_in)
        self._Vt = _in

    @property
    def mobility(self):
        return self._mobility

    @mobility.setter
    def mobility(self, _in):
        assert_value(_in)
        self._mobility = _in

    @property
    def max_gm(self):
        return self._max_gm

    @max_gm.setter
    def max_gm(self, _in):
        if isinstance(_in, np.ndarray):
            _in = self.max_value(_in)
        assert_value(_in)
        # assert isinstance(_in, Value)
        # if _in.unit.dimensionality !=
        self._max_gm = _in

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
            _in = self.min_value(_in)
        self._min_ss = _in

    @property
    def max_Ion(self):
        return self._max_Ion

    @max_Ion.setter
    def max_Ion(self, _in):
        assert_value(_in)
        if _in.unit.dimensionality != ureg.amp/ureg.meter:
            _in/self.width
        self._max_Ion = _in

    @property
    def max_Ion_n(self):
        return self._max_Ion_n

    @max_Ion_n.setter
    def max_Ion_n(self, _in):
        assert_value(_in)
        self._max_Ion_n = _in

    @property
    def max_Ion_Vd(self):
        return self._max_Ion_Vd

    @max_Ion_Vd.setter
    def max_Ion_Vd(self, _in):
        assert_value(_in)
        self.max_Ion_F = self.norm_Field(_in)
        self._max_Ion_Vd = _in

    @property
    def max_Ion_F(self):
        return self._max_Ion_F

    @max_Ion_F.setter
    def max_Ion_F(self, _in):
        assert_value(_in)
        self._max_Ion_F = _in

    @property
    def max_Ion_Vg(self):
        return self._max_Ion_Vg

    @max_Ion_Vg.setter
    def max_Ion_Vg(self, _in):
        assert_value(_in)
        self.max_Ion_n = self.vg_to_n(_in)
        self._max_Ion_Vg = _in

    def max_value(self, array):
        raise NotImplementedError('You must implement max_value')

    def min_value(self, array):
        raise NotImplementedError('You must implement max_value')


class NFET(FET):

    def __init__(self, *args, **kwargs):
        super(NFET, self).__init__(*args, **kwargs)

    def norm_Id(self, Id):
        # should not have to adjust anything
        return super(NFET, self).norm_Id(Id)

    def max_value(self, array):
        return abs(array).max()

    def min_value(self, array):
        return abs(array).min()


class PFET(FET):

    def __init__(self, *args, **kwargs):
        super(PFET, self).__init__(*args, **kwargs)

    def norm_Id(self, Id):
        # should not have to adjust anything
        return super(PFET, self).norm_Id(Id)

    # def norm_Vg(self, vg):
    #     return vg*-1

    def max_value(self, array):
        return abs(array).max()

    def min_value(self, array):
        return abs(array).min()
