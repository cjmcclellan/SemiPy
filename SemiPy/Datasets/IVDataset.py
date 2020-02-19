"""
DataSet for IdVg data
"""
from SemiPy.Datasets.Dataset import SetDataSet
from SemiPy.config.globals import common_drain_current_names, common_drain_voltage_names, common_gate_current_names, common_gate_voltage_names,\
    common_source_current_names, common_source_voltage_names
import numpy as np
from physics.value import Value, ureg


class IVDataSet(SetDataSet):

    master_independent = None
    secondary_independent = None
    secondary_independent_unit = None

    master_dependent = None

    column_names = ['vd', 'id', 'vg', 'ig', 'vs', 'is']
    column_units = [ureg.volt, ureg.amp, ureg.volt, ureg.amp, ureg.volt, ureg.amp]

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
        self.sweep_number = change_i.shape[1]
        assert self.sweep_number < 3, 'IV sweeps can only have a single direction or a forward and backward.' \
                                      '  Yours has {0} sweep directions'.format(change_i.shape[1])
        assert np.all(change_i[:, 1] == change_i[1, 1]), 'All IV sweeps must have the same number of x data points'
        # now save the change point
        self.change_i = change_i[1, 1] + 1

        # now convert the secondary independents to values
        self._convert_secondary_independent_to_value()

        # convert all the columns to Values
        for column, unit in zip(self.column_names, self.column_units):
            if self.gathered_column_names[column] is not None:
                self.adjust_column(column, func=self._convert_to_value(unit=unit))

    def _convert_to_value(self, unit):
        # creates a lambda function for converting values to a unit
        return lambda x: Value.array_like(x, unit=unit)

    def _check_fwd_bwd(self, column_name):
        # check if fwd or bwd are in the column name
        if '_fwd' in column_name:
            if self.sweep_number == 1:
                raise ValueError('You are attempting to access the forward sweep for this IV dataset,'
                                 'but there is only 1 sweep direction.')
            return column_name[:-4], True, False
        elif '_bwd' in column_name:
            if self.sweep_number == 1:
                raise ValueError('You are attempting to access the backward sweep for this IV dataset,'
                                 'but there is only 1 sweep direction.')
            return column_name[:-4], False, True
        else:
            return column_name, False, False

    def get_column(self, column_name, return_set_values=False):
        # add logic to deal with fwd and bwd requests
        column_name, fwd, bwd = self._check_fwd_bwd(column_name)
        column_data = super(IVDataSet, self).get_column(column_name, return_set_values)

        if fwd:
            column_data = column_data[..., :self.change_i]
        elif bwd:
            column_data = column_data[..., self.change_i:]

        return column_data

    def get_column_set(self, column_name, secondary_value):
        column_name, fwd, bwd = self._check_fwd_bwd(column_name)

        column_data = super(IVDataSet, self).get_column_set(column_name, secondary_value)

        if fwd:
            column_data = column_data[..., :self.change_i]
        elif bwd:
            column_data = column_data[..., self.change_i:]

        return column_data

    def _convert_secondary_independent_to_value(self):
        # converts the keys in the secondary independent dict to values
        secondary_value_unit = self.column_units[self.column_names.index(self.secondary_independent)]
        self.secondary_indep_values = {Value(value=key, unit=secondary_value_unit): val
                                       for key, val in self.secondary_indep_values.items()}


class IdVgDataSet(IVDataSet):

    master_independent = 'vg'
    secondary_independent = 'vd'

    master_dependent = 'id'


class IdVdDataSet(IVDataSet):

    master_independent = 'vd'
    secondary_independent = 'vg'

    master_dependent = 'id'

