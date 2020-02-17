"""
Extractor for extracting information of Field-Effect Transistors from IdVg and IdVd data sets
"""
from Extractions.Extractors.Extractors import Extractor
from Extractions.Datasets.IVDataset import IdVgDataSet, IdVdDataSet
from Extractions.Devices.FET.Transistor import NFET, PFET
from physics.value import Value, ureg
import warnings
import numpy as np
from Extractions.helper.plotting import create_scatter_plot


class FETExtractor(Extractor):

    def __init__(self, length, width, tox, epiox, device_polarity, idvd_path=None, idvg_path=None, *args, **kwargs):
        """
        An extractor object for Field-Effect Transistors (FETs).  To get FET properties, IdVd, or IdVg data, use the FET, idvd, and idvg
        attributes.  Look at FET, IdVgDataSet, and IdVdDataSet classes for understanding how to use these attributes.
        Args:
            length (Value or float):  Physical length of the FET.  Should be a Value with correct units or float in micrometers.
            width (Value or float): Physical length of the FET.  Should be a Value with correct units or float in micrometers.
            tox (Value or float): Physical thickness of the FET oxide.  Should be a Value with correct units or float in nanometers.
            epiox (Value or float): Dielectric constant of the oxide.  Should be a Value or float (unitless).
            device_polarity (str): The polarity of the device, either 'n' or 'p' for elector or hole, respectively.
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
            self.idvg = IdVgDataSet(data_path=idvg_path)

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
        a = 5

        # now normalize all the data in idvg and idvd
        adjust_current = lambda x: self.FET.norm_Id(Value.array_like(x * 1e6, unit=ureg.microamp))
        adjust_volt = lambda x: Value.array_like(x, unit=ureg.volt)

        if self.idvg is not None:
            self.idvg.adjust_column('id', func=adjust_current)
            self.idvg.adjust_column('vg', func=adjust_volt)
            self.idvg.adjust_column('vd', func=adjust_volt)

        if self.idvd is not None:
            self.idvd.adjust_column('id', func=adjust_current)
            self.idvd.adjust_column('vg', func=adjust_volt)
            self.idvd.adjust_column('vd', func=adjust_volt)

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
        Vd = self.idvg.get_secondary_indep_values()
        max_vd = max(Vd)
        max_vg = self.FET.max_value(self.idvg.get_column_set('vg_bwd', max_vd))
        # compute the gm
        gm_bwd = self._slope(x_data=self.idvg.get_column_set('vg_bwd', max_vd), y_data=self.idvg.get_column_set('id_bwd', max_vd))
        gm_fwd = self._slope(x_data=self.idvg.get_column_set('vg_fwd', max_vd), y_data=self.idvg.get_column_set('id_fwd', max_vd))
        # gm = np.concatenate((gm_fwd, gm_bwd), axis=-1)
        # repeat the last value so the shape matches
        # gm = np.concatenate((gm, gm[:, -1:]), axis=-1)
        # self.idvg.add_column(column_name='gm', column_data=gm)
        # get the max fwd and bwd gm and indexs
        max_gm_fwd, max_gm_fwd_i = self.FET.max_slope_value(gm_fwd, return_index=True)
        max_gm_bwd, max_gm_bwd_i = self.FET.max_slope_value(gm_bwd, return_index=True)

        # if the max gm is the last point, then warn the user that the gm has not turned over and the Vt extraction may have error
        if max_gm_fwd_i == gm_fwd.shape[0]:
            warnings.warn('The transconductance (gm) has not reached maximum by Vd of {0} and Vg of {1}, meaning there will be error in '
                          'the threshold voltage'.format(max_vd, max_vg))
        if max_gm_bwd_i == 0:
            warnings.warn('The transconductance (gm) has not reached maximum by Vd of {0} and Vg of {1}, meaning there will be error in '
                          'the threshold voltage'.format(max_vd, max_vg))

        self.FET.max_gm = self.FET.max_slope_value(Value.array_like(np.array([max_gm_bwd, max_gm_fwd]), unit=max_gm_fwd.unit))
        self.FET.max_gm_Vd = Value(max_vd, ureg.volt)

        _, b, Vt_fwd = self._linear_extraction(y=self.idvg.get_column_set('id_fwd', secondary_value=max_vd)[max_gm_fwd_i],
                                               x=self.idvg.get_column_set('vg_fwd', secondary_value=max_vd)[max_gm_fwd_i],
                                               slope=max_gm_fwd)

        _, b, Vt_bwd = self._linear_extraction(y=self.idvg.get_column_set('id_bwd', secondary_value=max_vd)[max_gm_bwd_i],
                                               x=self.idvg.get_column_set('vg_bwd', secondary_value=max_vd)[max_gm_bwd_i],
                                               slope=max_gm_bwd)

        self.FET.Vt_fwd = Vt_fwd
        self.FET.Vt_bwd = Vt_bwd

        # compute the ss
        ss = self._slope(y_data=self.idvg.get_column('vg'), x_data=np.log10(self.idvg.get_column('id')))
        ss = np.concatenate((ss, ss[:, -1:]), axis=-1)
        self.idvg.add_column(column_name='ss', column_data=ss)
        self.FET.min_ss = ss

        self.FET.compute_properties()

    @staticmethod
    def __check_properties(length, width, tox, epiox):
        # make sure given properties are values
        if not isinstance(length, Value):
            warnings.warn('Given length is not a value. Assuming units are micrometers.')
            length = Value(value=length, unit=ureg.micrometer)
        else:
            assert length.unit == ureg.meter, 'Your length is not given in meters, but {0}.'.format(length.unit)

        if not isinstance(width, Value):
            warnings.warn('Given width is not a value. Assuming units are micrometers.')
            width = Value(value=width, unit=ureg.micrometer)
        else:
            assert width.unit == ureg.meter, 'Your length is not given in meters, but {0}.'.format(width.unit)

        if not isinstance(tox, Value):
            warnings.warn('Given Tox is not a value. Assuming units are nanometers.')
            tox = Value(value=tox, unit=ureg.nanometer)
        else:
            assert tox.unit == ureg.meter, 'Your length is not given in meters, but {0}.'.format(tox.unit)

        if not isinstance(epiox, Value):
            epiox = Value(value=epiox)

        # now return all the properties
        return length, width, tox, epiox
