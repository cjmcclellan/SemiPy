"""
DataSet for IdVg data
"""
from .Dataset import SetDataSet
from ..config.globals import common_drain_current_names, common_drain_voltage_names, common_gate_current_names, common_gate_voltage_names,\
    common_source_current_names, common_source_voltage_names
import numpy as np


class IVDataSet(SetDataSet):

    master_independent = None
    secondary_independent = None

    master_dependent = None

    column_names = ['vd', 'id', 'vg', 'ig', 'vs', 'is']

    def __init__(self, drainv=None, draini=None, gatev=None, gatei=None, sourcei=None, sourcev=None, *args, **kwargs):
        """
        DataSet for IV data.  The master and secondary independent variables and the master dependent variable are defined child classes.
        The secondary variable is varied between columns sets (if there are multiple column sets). For example, in an IdVg dataset the
        master variable is Vg and different column sets are typically defined by different Vd values, so Vd is the secondary variable.
        Args:
            *args:
            **kwargs:
        """
        # get the column names for the Vd, Id, Vg, Ig, Vs, Is columns. If there are multiple, save corresponding to the secondary variable.
        given_column_names = [drainv, draini, gatev, gatei, sourcev, sourcei]
        common_column_names = [common_drain_voltage_names, common_drain_current_names, common_gate_voltage_names, common_gate_current_names,
                               common_source_voltage_names, common_source_current_names]

        super(IVDataSet, self).__init__(given_column_names=given_column_names, common_column_names=common_column_names, *args, **kwargs)

        # now divide the data into fwd, bwd sweeps, if they exist
        # get the args where the master independent changes sign.  If there are multiple for each row, raise an error
        change_i = np.argwhere(np.diff(self.get_column(self.master_independent)) == 0.0)
        assert change_i.shape[1] < 3, 'IV sweeps can only have a single direction or a forward and backward.' \
                                      '  Yours has {0} sweep directions'.format(change_i.shape[1])
        assert np.all(change_i[:, 1] == change_i[1, 1]), 'All IV sweeps must have the same number of x data points'

        # now break up all the sets into fwd and bwd sweeps
        if change_i.shape[1] == 2:
            self.super_gathered_column_names['id'] = ['id_fwd', 'id_bwd']
            self.gathered_column_names['id_fwd'] = self.gathered_column_names['id']
            self.gathered_column_names['id_bwd'] = self.gathered_column_names['id']
            self.gathered_column_names.pop('id')


class IdVgDataSet(IVDataSet):

    master_independent = 'vg'
    secondary_independent = 'vd'

    master_dependent = 'id'


class IdVdDataSet(IVDataSet):

    master_independent = 'vd'
    secondary_independent = 'vg'

    master_dependent = 'id'
