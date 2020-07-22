"""
DataSet for IdVg data
"""
from SemiPy.Datasets.Dataset import SetDataSet
from SemiPy.config.globals import common_drain_current_names, common_drain_voltage_names, common_gate_current_names, common_gate_voltage_names,\
    common_source_current_names, common_source_voltage_names
import numpy as np
from physics.value import Value, ureg


class BiDirectionalDataSet(SetDataSet):

    master_independent = None
    secondary_independent = None

    master_dependent = None

    column_names = []
    column_units = []

    def __init__(self, given_column_names=None, common_column_names=None, *args, **kwargs):
        """
        DataSet for IV data.  The master and secondary independent variables and the master dependent variable are defined child classes.
        The secondary variable is varied between columns sets (if there are multiple column sets). For example, in an IdVg dataset the
        master variable is Vg and different column sets are typically defined by different Vd values, so Vd is the secondary variable.
        Args:
            *args:
            **kwargs:
        """
        if common_column_names is None:
            common_column_names = self.column_names
        super(BiDirectionalDataSet, self).__init__(given_column_names=given_column_names, common_column_names=common_column_names, *args, **kwargs)

        # now divide the data into fwd, bwd sweeps, if they exist
        # get the args where the master independent changes sign.  If there are multiple for each row, raise an error
        # change_i = np.argwhere(np.diff(np.array(self.get_column(self.master_independent), dtype=np.float)) == 0.0)
        change_i = self._get_sweep_index()
        self.sweep_number = ((change_i.shape[0]) / self.num_secondary_indep_sets) + 1
        assert self.sweep_number < 3, 'IV sweeps can only have a single direction or a forward and backward.' \
                                      '  Yours has {0} sweep directions'.format(self.sweep_number)

        assert np.all(change_i[:, 1] == change_i[1, 1]), 'All IV sweeps must have the same number of x data points'
        # now save the change point
        self.change_i = change_i[1, 1]

        # now convert the secondary independents to values
        self._convert_secondary_independent_to_value()

        # convert all the columns to Values
        for column, unit in zip(self.column_names, self.column_units):
            if self.gathered_column_names[column] is not None and not isinstance(self.get_column(column).flat[0], Value):
                self.adjust_column(column, func=self._convert_to_value(unit=unit))

    @staticmethod
    def _convert_to_value(unit):
        # creates a lambda function for converting values to a unit
        return lambda x: Value.array_like(x, unit=unit)

    def _get_sweep_index(self, array=None):
        """
        Get the index where the sweep direction changes
        Args:
            array (np.ndarray): Defaults to the master_independent column data unless a different array is givem

        Returns:
            np.ndarray with all the index points of change in sweep direction
        """
        if array is None:
            array = np.array(self.get_column(self.master_independent), dtype=np.float)
        else:
            array = np.array(array, dtype=np.float)
        # this formula will find the point of change in sweep direction accounting for duplicate final points i.e. Vg = [1, 2, 3, 3, 2, 1] => change_i = [2]
        change_i = np.argwhere(np.abs(np.diff(np.sign(array[..., 2:] - array[..., :-2]))) == 2.0) + 1
        return change_i + 1

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

    def get_column(self, column_name, return_set_values=False, master_independent_value_range=None):
        """

        Args:
            column_name:
            return_set_values:
            master_independent_value_range (list or None): List of range of desired values.

        Returns:

        """
        # add logic to deal with fwd and bwd requests
        column_name, fwd, bwd = self._check_fwd_bwd(column_name)

        column_data = super(BiDirectionalDataSet, self).get_column(column_name, return_set_values,
                                                                   master_independent_value_range)
        # if the column was indexed, we need to locate the new inflection point
        if master_independent_value_range is not None and (fwd or bwd):
            change_i = self._get_sweep_index(array=super(BiDirectionalDataSet, self).get_column(self.master_independent,
                                                                                                False, master_independent_value_range))
            # if no inflection point, then just return the column data
            if len(change_i) == 0:
                return column_data
            change_i = change_i[1, 1]
        elif fwd or bwd:
            change_i = self.change_i
        if fwd:
            column_data = column_data[..., :change_i]
        elif bwd:
            column_data = column_data[..., change_i:]

        return column_data

    def get_column_set(self, column_name, secondary_value):
        column_name, fwd, bwd = self._check_fwd_bwd(column_name)

        column_data = super(BiDirectionalDataSet, self).get_column_set(column_name, secondary_value)

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


class TLMDataSet(BiDirectionalDataSet):

    master_independent = 'n'
    secondary_independent = 'l'

    master_dependent = 'r'

    column_names = ['n', 'r', 'l']
    column_units = [ureg.centimeter ** -2, ureg.ohm * ureg.micrometer, ureg.micrometer]


class IVDataSet(BiDirectionalDataSet):

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

        given_column_names = [drainv, draini, gatev, gatei, sourcev, sourcei]
        common_column_names = [common_drain_voltage_names, common_drain_current_names, common_gate_voltage_names, common_gate_current_names,
                               common_source_voltage_names, common_source_current_names]

        super(IVDataSet, self).__init__(given_column_names=given_column_names, common_column_names=common_column_names, *args, **kwargs)


class IdVgDataSet(IVDataSet):

    master_independent = 'vg'
    secondary_independent = 'vd'

    master_dependent = 'id'


class IdVdDataSet(IVDataSet):

    master_independent = 'vd'
    secondary_independent = 'vg'

    master_dependent = 'id'

