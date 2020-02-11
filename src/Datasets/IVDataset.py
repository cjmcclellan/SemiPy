"""
DataSet for IdVg data
"""
from .Dataset import BaseDataSet
from ..config.globals import common_drain_current_names, common_drain_voltage_names, common_gate_current_names, common_gate_voltage_names,\
    common_source_current_names, common_source_voltage_names
import warnings


class IVDataSet(BaseDataSet):

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
        super(IVDataSet, self).__init__(*args, **kwargs)

        # get the column names for the Vd, Id, Vg, Ig, Vs, Is columns. If there are multiple, save corresponding to the secondary variable.
        given_column_names = [drainv, draini, gatev, gatei, sourcev, sourcei]
        common_column_names = [common_drain_voltage_names, common_drain_current_names, common_gate_voltage_names, common_gate_current_names,
                               common_source_voltage_names, common_source_current_names]
        column_names = ['vd', 'id', 'vg', 'ig', 'vs', 'is']

        # loop th  rough all the column names
        for i in range(len(column_names)):
            # if no column name was given, then try to use common column names
            if given_column_names[i] is None:
                names = self._find_similar_column(common_column_names[i])
            else:
                names = self._find_similar_column(given_column_names[i])

            if names is None:
                assert not (column_names[i] is self.master_dependent or column_names[i] is self.master_independent),\
                    'Cannot find the column for {0}'.format(column_names[i])
                warnings.warn('Cannot find the column for {0} in the dataset'.format(column_names[i]))

            self.__dict__[column_names[i]] = names

        a = 5


class IdVgDataSet(IVDataSet):

    master_variable = 'Vg'
    secondary_variable = 'Vd'

    master_dependent = 'Id'


class IdVdDataSet(IVDataSet):

    master_variable = 'Vd'
    secondary_variable = 'Vg'

    master_dependent = 'Id'
