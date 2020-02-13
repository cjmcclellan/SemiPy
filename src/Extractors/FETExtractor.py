"""
Extractor for extracting information of Field-Effect Transistors from IdVg and IdVd data sets
"""
from .Extractors import Extractor
from ..Datasets.IVDataset import IdVgDataSet, IdVdDataSet
from ..Devices.FET.Transistor import NFET, PFET
from physics.value import Value, ureg
import warnings
import numpy as np
from ..helper.plotting import create_scatter_plot


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
        adjust_current = lambda x: self.FET.norm_Id(Value.array_like(x, unit=ureg.amp))
        self.idvg.adjust_column('id', func=adjust_current)
        self.idvd.adjust_column('id', func=adjust_current)

        adjust_volt = lambda x: Value.array_like(x, unit=ureg.volt)
        self.idvg.adjust_column('vg', func=adjust_volt)
        self.idvg.adjust_column('vd', func=adjust_volt)
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
        # compute the gm
        gm = self._slope(x_data=self.idvg.get_column('vg'), y_data=self.idvg.get_column('id'))
        # repeat the last value so the shape matches
        gm = np.concatenate((gm, gm[:, -1:]), axis=-1)
        self.idvg.add_column(column_name='gm', column_data=gm)
        self.FET.max_gm = gm

        # compute the ss
        ss = self._slope(y_data=self.idvg.get_column('vg'), x_data=np.log10(self.idvg.get_column('id')))
        ss = np.concatenate((ss, ss[:, -1:]), axis=-1)
        self.idvg.add_column(column_name='ss', column_data=ss)
        self.FET.min_ss = ss




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
