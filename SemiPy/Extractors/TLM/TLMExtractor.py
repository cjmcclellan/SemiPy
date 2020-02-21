"""
Extractor for extracting information of from TLM data
"""
from SemiPy.Extractors.Extractors import Extractor
from SemiPy.Datasets.IVDataset import TLMDataSet
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
from physics.value import Value, ureg
import os
from SemiPy.helper.math import find_nearest_arg
import warnings
import numpy as np
import pandas as pd


class TLMExtractor(Extractor):

    def __init__(self, lengths, widths, tox, epiox, device_polarity, vd_values=None, idvg_path=None, *args, **kwargs):
        """
        An extractor object for Field-Effect Transistors (FETs).  To get FET properties, IdVd, or IdVg data, use the FET, idvd, and idvg
        attributes.  Look at FET, IdVgDataSet, and IdVdDataSet classes for understanding how to use these attributes.
        Args:
            length (list):  The list of the physical FET length.  Should be Values with correct units for floats in micrometers
            width (Value, float, or list): Physical width of the FET.  Should be a Value with correct units or float in micrometers.
            tox (Value or float): Physical thickness of the FET oxide.  Should be a Value with correct units or float in nanometers.
            epiox (Value or float): Dielectric constant of the oxide.  Should be a Value or float (unitless).
            device_polarity (str): The polarity of the device, either 'n' or 'p' for electron or hole, respectively.
            idvg_path (str): Path to the folder with all the IdVg data.
            *args:
            **kwargs:
        """
        super(TLMExtractor, self).__init__(*args, **kwargs)

        # now create FETExtractors for every set of IdVg data
        self.FETs = []
        self.data_dict = {'n': [], 'r': [], 'l': []}
        self.n_max = []

        self.vd_values = None

        for root, dirs, idvg_data in os.walk(idvg_path):
            # make sure there are lengths for each data file
            assert len(lengths) == len(idvg_data), 'There are too many or too few channel lengths given for the data.'
            for i, idvg in enumerate(idvg_data):
                path = os.path.join(root, idvg)
                self.FETs.append(FETExtractor(width=widths, length=lengths[i], epiox=epiox, tox=tox,
                                              device_polarity=device_polarity, idvg_path=path,
                                              vd_values=vd_values))

                new_fet_vd_values = self.FETs[-1].idvg.get_secondary_indep_values()

                if self.vd_values is None:
                    self.vd_values = new_fet_vd_values

                assert new_fet_vd_values == self.vd_values,\
                    'The IdVg data at {0} for this TLM does not have consistent Vd values.' \
                    '  Make sure that all the Vd values are the same for every dataset'.format(idvg_path)

                # grab the n and resistances
                self.data_dict['n'].append(self.FETs[-1].idvg.get_column('n'))
                self.n_max.append(np.max(self.data_dict['n'][-1], axis=-1))
                self.data_dict['r'].append(self.FETs[-1].idvg.get_column('resistance'))
                self.data_dict['l'].append(np.ones_like(self.data_dict['n'][-1]) * self.FETs[-1].FET.length)

        # now lets start processing the data, first creating a TLMDataSet for each Vd value
        self.tlm_datasets = {}
        # convert to np arrays for easy indexing
        self.data_dict = {key: np.array(data) for key, data in self.data_dict.items()}

        for i, vd in enumerate(self.vd_values):
            new_dataset = TLMDataSet(data_path=pd.DataFrame.from_dict({key + '_' + str(j): self.data_dict[key][j, i, :]
                                                                       for j in range(len(lengths))
                                                                       for key in ('n', 'r', 'l')}))
            self.tlm_datasets[vd] = new_dataset

            # now we can start computing TLM properties
            min_max_n = np.min(np.array(self.n_max)[:, i])
            n_fwd = new_dataset.get_column('n')
            nearest_max_n_i = find_nearest_arg(n, min_max_n, axis=-1)

            # now get the range of n
            above_zero_i =

            a = 5

