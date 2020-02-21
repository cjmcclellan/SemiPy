"""
Extractor for extracting information of Field-Effect Transistors from IdVg and IdVd data sets
"""
from SemiPy.Extractors.Extractors import Extractor
from SemiPy.Datasets.IVDataset import IdVgDataSet, IdVdDataSet
from SemiPy.Devices.FET.Transistor import NFET, PFET
from physics.value import Value, ureg
import warnings
import numpy as np
from SemiPy.helper.plotting import create_scatter_plot


class FETExtractor(Extractor):

    def __init__(self, length, width, tox, epiox, device_polarity, vd_values=None, idvd_path=None, idvg_path=None, *args, **kwargs):
        """
        An extractor object for Field-Effect Transistors (FETs).  To get FET properties, IdVd, or IdVg data, use the FET, idvd, and idvg
        attributes.  Look at FET, IdVgDataSet, and IdVdDataSet classes for understanding how to use these attributes.
        Args:
            length (Value or float):  Physical length of the FET.  Should be a Value with correct units or float in micrometers.
            width (Value or float): Physical width of the FET.  Should be a Value with correct units or float in micrometers.
            tox (Value or float): Physical thickness of the FET oxide.  Should be a Value with correct units or float in nanometers.
            epiox (Value or float): Dielectric constant of the oxide.  Should be a Value or float (unitless).
            device_polarity (str): The polarity of the device, either 'n' or 'p' for electron or hole, respectively.
            idvd_path (str): Path to the IdVd data.
            idvg_path (str): Path to the IdVg data.
            *args:
            **kwargs:
        """

        super(FETExtractor, self).__init__(*args, **kwargs)

        # import the idvg and idvd path if given
        if idvd_path is None and idvg_path is None:
            raise ValueError('You have not given a path to IdVd or IdVg data, so there is nothing to extract')

        if idvg_path is None:
            self.idvg = None
        else:
            self.idvg = IdVgDataSet(data_path=idvg_path, secondary_independent_values=vd_values)

        if idvd_path is None:
            self.idvd = None
        else:
            self.idvd = IdVdDataSet(data_path=idvd_path)

        # now check the given properties
        length, width, tox, epiox = self.__check_properties(length, width, tox, epiox)

        # now create the FET model
        if device_polarity is 'p':
            self.FET = PFET(length=length, width=width, tox=tox, dielectric_const=epiox)
        elif device_polarity is 'n':
            self.FET = NFET(length=length, width=width, tox=tox, dielectric_const=epiox)
        else:
            raise ValueError('The device polarity must be either n or p, not {0}'.format(device_polarity))

        # add some simple checks on the data.  Make sure Ig is not too high, Is and Id are reasonably matched, etc.

        # now normalize all the data in idvg and idvd
        adjust_current = lambda x: self.FET.norm_Id(x)
        # adjust_volt = lambda x: Value.array_like(x, unit=ureg.volt)

        if self.idvg is not None:
            self.idvg.adjust_column('id', func=adjust_current)

        if self.idvd is not None:
            self.idvd.adjust_column('id', func=adjust_current)

        # now run the extractions
        self.__extract_data()

    def __extract_data(self):
        """
        Extract the properties of the FET given the available data, including transconductance (gm), subthreshold swing (ss), field-effect
        mobility (mufe), threshold voltage (vt), max on current (max_Ion), min off current at max Ion Vd (min_Ioff),
        Returns:
            None
        """

        # now compute the vt and gm using the max Vd
        vd = self.idvg.get_secondary_indep_values()
        # adjust the shape to be [num_set, 1]
        vd = Value.array_like(np.expand_dims(np.array(vd), axis=-1), unit=ureg.volt)
        max_vd = max(vd)

        vg = self.idvg.get_column('vg')
        max_vg = self.FET.max_value(vg)

        # get the max and min Ion
        ion = self.idvg.get_column('id')
        max_ion, max_ion_i = self.FET.max_value(ion, return_index=True)
        max_ion_vd = vd[max_ion_i[0], 0]
        max_ion_vg = vg[max_ion_i]
        self.FET.max_Ion.set(prop_value=max_ion, input_values={'Vg': max_ion_vg, 'Vd': max_ion_vd})

        # compute the gm
        gm_fwd, max_gm_fwd, max_gm_fwd_i = self._extract_gm(fwd=True, return_max=True)
        gm_bwd, max_gm_bwd, max_gm_bwd_i = self._extract_gm(bwd=True, return_max=True)

        gm = np.concatenate((gm_fwd, gm_bwd), axis=-1)

        self.idvg.add_column(column_name='gm', column_data=gm)

        max_gm, max_gm_i = self.FET.max_slope_value(self.idvg.get_column(column_name='gm'), return_index=True)
        max_gm_vd = vd[max_gm_i[0], 0]
        max_gm_input_values = {'Vg': self.idvg.get_column_set('vg', max_gm_vd)[max_gm_i[-1]], 'Vd': max_gm_vd}

        self.FET.max_gm.set(max_gm, max_gm_input_values)

        # Now extract the Vt values
        vt_fwd = self._extract_vt(index=max_gm_fwd_i, max_gm=max_gm_fwd, fwd=True)
        vt_bwd = self._extract_vt(index=max_gm_bwd_i, max_gm=max_gm_bwd, bwd=True)

        self.FET.Vt_fwd.set(vt_fwd)
        self.FET.Vt_bwd.set(vt_bwd)

        # compute the ss
        ss = self._slope(y_data=self.idvg.get_column('vg'),
                         x_data=np.log10(self.idvg.get_column('id')),
                         keep_dims=True)
        self.idvg.add_column(column_name='ss', column_data=ss)
        self.FET.min_ss = ss

        self.FET.compute_properties()

        # now compute the carrier density
        n = self.FET.vg_to_n(self.idvg.get_column('vg'))
        self.idvg.add_column('n', n)

        # now compute the resistance
        r = vd / self.idvg.get_column('id')
        self.idvg.add_column('resistance', r)

    # def extract_double_sweep(self, ):

    def _extract_gm(self, fwd=False, bwd=False, vd=None, return_max=False):
        current, gate = self._sweep_directions(['id', 'vg'], fwd=fwd, bwd=bwd)

        if vd is None:
            gm = self._slope(x_data=self.idvg.get_column(gate),
                             y_data=self.idvg.get_column(current), keep_dims=True)
        else:
            gm = self._slope(x_data=self.idvg.get_column_set(gate, vd),
                             y_data=self.idvg.get_column_set(current, vd), keep_dims=True)

        # if return max, then return the max and max_i
        if return_max:
            max_gm, max_gm_i = self.FET.max_slope_value(gm, return_index=True)

            # now check if the max gm was reached before the final Vg point.  If so, then there could be error
            vg = self.idvg.get_column('vg')
            max_vg = self.FET.max_slope_value(vg)
            if max_vg == vg[max_gm_i]:
                warnings.warn('The transconductance (gm) has not reached maximum, potentially resulting in error'
                              ' in extracting threshold voltage')

            return gm, max_gm, max_gm_i
        else:
            return gm

    def _extract_vt(self, index, max_gm, fwd=False, bwd=False, vd=None):
        current, gate = self._sweep_directions(['id', 'vg'], fwd=fwd, bwd=bwd)

        if vd is None:
            current = self.idvg.get_column(current)[index]
            gate = self.idvg.get_column(gate)[index]
        else:
            current = self.idvg.get_column_set(current, secondary_value=vd)[index]
            gate = self.idvg.get_column_set(gate, secondary_value=vd)[index]

        _, _, vt = self._linear_extraction(y=current, x=gate, slope=max_gm)
        return vt

    def _sweep_directions(self, keys, fwd=False, bwd=False):
        """
        Adjust the keys of columns to index fwd or bwd.
        Args:
            keys (list): The list of strs of the columns to be accessed
            fwd (bool): Flag for if fwd should be accessed
            bwd (bool): Flag for if bwd should be accessed

        Returns:
            tuple of keys adjusted (or not if both fwd and bwd are false)
        """
        if fwd:
            keys = [key + '_fwd' for key in keys]
        elif bwd:
            keys = [key + '_bwd' for key in keys]

        return tuple(keys)

    @staticmethod
    def __check_properties(length, width, tox, epiox):
        # make sure given properties are values
        if not isinstance(length, Value):
            warnings.warn('Given length is not a value. Assuming units are micrometers.')
            length = Value(value=length, unit=ureg.micrometer)
        else:
            assert length.unit.dimensionality == ureg.meter.dimensionality, 'Your length is not given in meters, but {0}.'.format(length.unit.dimensionality)

        if not isinstance(width, Value):
            warnings.warn('Given width is not a value. Assuming units are micrometers.')
            width = Value(value=width, unit=ureg.micrometer)
        else:
            assert width.unit.dimensionality == ureg.meter.dimensionality, 'Your length is not given in meters, but {0}.'.format(width.unit.dimensionality)

        if not isinstance(tox, Value):
            warnings.warn('Given Tox is not a value. Assuming units are nanometers.')
            tox = Value(value=tox, unit=ureg.nanometer)
        else:
            assert tox.unit.dimensionality == ureg.meter.dimensionality, 'Your length is not given in meters, but {0}.'.format(tox.unit.dimensionality)

        if not isinstance(epiox, Value):
            epiox = Value(value=epiox)

        # now return all the properties
        return length, width, tox, epiox
