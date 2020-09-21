"""
Extractor for extracting information of from TLM data
"""
from SemiPy.Extractors.Extractors import Extractor
from SemiPy.Datasets.IVDataset import TLMDataSet
from SemiPy.Devices.Devices.FET.Transistor import FET
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
from physics.value import Value, ureg
import os
from SemiPy.helper.math import find_nearest_arg
import warnings
from SemiPy.helper.plotting import create_scatter_plot
import numpy as np
import pandas as pd
from dash_cjm.plots.Basic import BasicPlot


class TLMExtractor(Extractor):
    """
    An extractor object for Transfer Length Method (TLM) measurements.

    Args:
        length (list):  The list of the physical FET length.  Should be Values with correct units for floats in micrometers
        width (Value, float, or list): Physical width of the FET.  Should be a Value with correct units or float in micrometers.
        tox (Value or float): Physical thickness of the FET oxide.  Should be a Value with correct units or float in nanometers.
        epiox (Value or float): Dielectric constant of the oxide.  Should be a Value or float (unitless).
        device_polarity (str): The polarity of the device, either 'n' or 'p' for electron or hole, respectively.
        idvg_path (str): Path to the folder with all the IdVg data.

    Attributes:
        tlm_datasets: A dict of SemiPy.Datasets.IVDataset.TLMDataSet indexed by Vd values
        FETs: A list of all the SemiPy.Devices.FET.Transistor.FETs analyzed from the IdVg data

    Example:
        Example of how to extract TLM data from IdVg data

        >>> from physics.value import Value, ureg
        # path points to a folder with all the IdVg data
        >>> widths = Value(4.0, ureg.micrometer)
        >>> lengths = Value.array_like(np.array([1.0, 0.5, 2.0]), unit=ureg.micrometer)
        >>> tox = Value(90, ureg.nanometer)
        >>> tlm = TLMExtractor(widths=widths, lengths=lengths, tox=tox, epiox=3.9, device_polarity='n', idvg_path=path, vd_values=[1.0, 2.0])
        # save all the plots of the TLM
        >>> tlm.save_tlm_plots()
    """

    maximum_n_varience = Value(8e11, ureg.centimeter ** -2)

    def __init__(self, lengths, widths, channel, gate_oxide, FET_class, vd_values=None, idvg_path=None, *args, **kwargs):

        super(TLMExtractor, self).__init__()

        # now create FETExtractors for every set of IdVg data
        self.FETs = []
        self.data_dict = {'n': [], 'r': [], 'l': []}
        self.n_max = []

        self.vd_values = vd_values

        for root, dirs, idvg_data in os.walk(idvg_path):
            # make sure there are lengths for each data file
            assert len(lengths) == len(idvg_data), 'There are too many or too few channel' \
                                                   ' lengths given for the data. ({0})'.format(idvg_data)
            for i, idvg in enumerate(idvg_data):
                path = os.path.join(root, idvg)

                fet = FET_class(gate_oxide=gate_oxide, channel=channel, width=widths, length=lengths[i], *args, **kwargs)
                self.FETs.append(FETExtractor(fet, idvg_path=path,
                                              vd_values=vd_values))
                # self.FETs.append(FETExtractor(width=widths, length=lengths[i], epiox=epiox, tox=tox,
                #                               device_polarity=device_polarity, idvg_path=path,
                #                               vd_values=vd_values))

                new_fet_vd_values = self.FETs[-1].idvg.get_secondary_indep_values()

                if self.vd_values is None:
                    self.vd_values = new_fet_vd_values

                assert new_fet_vd_values == self.vd_values,\
                    'The IdVg data at {0} for this TLM does not have consistent Vd values.' \
                    '  Make sure that all the Vd values are the same for every dataset'.format(idvg_path)

                # grab the n and resistances and create the l column
                self.data_dict['n'].append(self.FETs[-1].idvg.get_column('n'))
                self.n_max.append(np.max(self.data_dict['n'][-1], axis=-1))
                self.data_dict['r'].append(self.FETs[-1].idvg.get_column('resistance'))
                self.data_dict['l'].append(np.ones_like(self.data_dict['n'][-1]) * self.FETs[-1].FET.length)

                # create_scatter_plot(self.FETs[-1].idvg.get_column('n')[0], self.FETs[-1].idvg.get_column('id')[-1], scale='lin', show=True, autoscale=True)

        # now lets start processing the data, first creating a TLMDataSet for each Vd value
        self.tlm_datasets = {}
        # convert to np arrays for easy indexing
        self.data_dict = {key: np.array(data) for key, data in self.data_dict.items()}

        # make sure there is actually data in the data_dict
        assert len(self.data_dict['n']) != 0, 'There is no data in the file path you gave.  Make sure the path is correct.'

        for i, vd in enumerate(self.vd_values):
            new_dataset = TLMDataSet(data_path=pd.DataFrame.from_dict({key + '_' + str(j): self.data_dict[key][j, i, :]
                                                                       for j in range(len(lengths))
                                                                       for key in ('n', 'r', 'l')}))
            self.tlm_datasets[vd] = new_dataset

    def save_tlm_plots(self):
        """
        Saves TLM plots for this TLM instance at all Vd values. This includes R vs. Length, Rc vs. n, Rsheet vs. n

        """
        for i, vd in enumerate(self.vd_values):

            new_dataset = self.tlm_datasets[vd]

            # now we can start computing TLM properties
            n_full = new_dataset.get_column('n')

            # get the column with the lowest max min
            min_max_n_col = np.argmin(np.max(n_full, axis=1))
            # get the min_max n value
            min_max_n = np.min(np.max(n_full, axis=1))
            # now get the min n value from the column with the min_max_n.  This is important to ensure we get a rectangular n array
            max_min_n = np.partition(n_full[min_max_n_col][np.where(n_full[min_max_n_col, :] >= 1.0)[0]], 2)[2]
            # value = 989429999999.9993 = 9.89e+11

            # expr: np.where((n_full[1]>max_min_n) & (n_full[1]<min_max_n))
            # looks like for n_full[1] range is 29-122 with gap 68-83 for total of 78 values
            # n_full[0]: 37-114, missing 75-76 for total 76 values
            # n_full[2]: 31-120, missing 68-83 for total 76 values
            n = new_dataset.get_column('n', master_independent_value_range=[max_min_n, min_max_n.magnitude])

            # check to make sure the n values are close enough.  If the Vg step is not fine enough and the device Vts are hihgly varied, the n values may not be close enough
            # to extract TLM data at a specific n
            max_n_varience = np.max(n[:, 1]) - np.min(n[:, 1])
            assert max_n_varience < self.maximum_n_varience, 'Varience in carrier density between the devices is {0}, which is greater than {1}.  As such,' \
                                                             'accurate TLM extraction is not possible.  This could be the result of too small a gate' \
                                                             'voltage step and high varience between device threshold voltages.  You can try to remove ' \
                                                             'device data with high varience, or lower the maximum_n_varience value in the' \
                                                             'TLMExtractor object.'.format(max_n_varience, self.maximum_n_varience)

            n_r = np.round(np.array(n, dtype=float) * 1e-12)
            r = new_dataset.get_column('r', master_independent_value_range=[max_min_n, min_max_n.magnitude])
            l = new_dataset.get_column('l', master_independent_value_range=[max_min_n, min_max_n.magnitude])

            n_units = '10<sup>12</sup> cm<sup>-2</sup>'
            r_units = '\u03A9\u2022\u03BCm'  # ;&times;&mu;m'
            l_units = '\u03BCm'
            # create_scatter_plot(l[:, 0], r[:, 0], scale='lin', show=True, autoscale=True)

            r_sheet, r_sheet_error, rc, rc_error = self.linear_regression(l, r)

            # now add r_sheet and rc to the dataset
            # new_dataset.add_column()
            max_l = float(max(l[:, 0]))

            r_plot = BasicPlot(x_label='length {0}'.format(l_units), y_label='total resistance {0}'.format(r_units), marker_size=8.0, x_min=0.0,
                               x_max=max_l * 1.2)

            for i in range(0, len(n[0]), round(len(n[0]) / 5)):
                r_plot.add_data(x_data=l[:, i], y_data=r[:, i], mode='markers', name='n = {0} {1}'.format(n_r[0][i], n_units), text='n')
                r_plot.add_line(x_data=[0.0, max_l], y_data=[float(rc[i]), float(r[-1, i])], name=None)

            #r_plot.save_plot(name='r_at_vd_{0}'.format(vd))

            rc_plot = BasicPlot(x_label='carrier density {0}'.format(n_units), y_label='contact resistance {0}'.format(r_units),
                                marker_size=8.0)

            rc_plot.add_data(x_data=n[0] * 1e-12, y_data=rc, error_y={'type': 'data', 'array': np.array(rc_error, dtype=float), 'visible': True},
                             mode='markers', name='n', text='n')

            #rc_plot.save_plot(name='rc_at_vd_{0}'.format(vd))

            rsheet_plot = BasicPlot(x_label='carrier density {0}'.format(n_units), y_label='sheet resistance', marker_size=8.0)

            rsheet_plot.add_data(x_data=n[0] * 1e-12, y_data=r_sheet, error_y={'type': 'data', 'array': np.array(r_sheet_error, dtype=float),
                                                                       'visible': True}, mode='markers', name='n', text='n')

            #rsheet_plot.save_plot(name='rsheet_at_vd_{0}'.format(vd))

