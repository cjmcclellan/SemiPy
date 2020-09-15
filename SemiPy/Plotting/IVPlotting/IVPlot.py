"""
IV Plotting Classes
"""
from SemiPy.Plotting.BasicPlot import BasicPlot
from SemiPy.Datasets.IVDataset import IdVdDataSet
from physics.value import Value, ureg, pint_to_str
import matplotlib.pyplot as plt


class IdVgPlot(BasicPlot):

    x_axis_title = '$V_G$'
    x_axis_scale = 'linear'
    x_units = ureg.volt

    y_axis_title = '$I_D$'
    y_axis_scale = 'linear'
    y_units = ureg.microampere / ureg.micrometer

    def __init__(self, *args, **kwargs):

        super(IdVgPlot, self).__init__(*args, **kwargs)
    #
    # def


class IdVdPlot(BasicPlot):

    x_axis_title = '$V_D$'
    x_axis_scale = 'linear'
    x_units = ureg.volt

    y_axis_title = '$I_D$'
    y_axis_scale = 'linear'
    y_units = ureg.microampere / ureg.micrometer

    def __init__(self, *args, **kwargs):

        super(IdVdPlot, self).__init__(*args, **kwargs)

    def add_idvd_dataset(self, dataset, *args, **kwargs):

        assert isinstance(dataset, IdVdDataSet), 'You must pass an IdVdDataSet class for IdVdPlots, not {0}'.format(type(dataset))

        # get the Vg values
        Vg_values = dataset.get_secondary_indep_values()
        Vd = dataset.get_column(dataset.master_independent)[0]

        for Vg in Vg_values:
            self.add_data(Vd, dataset.get_column_set('id', Vg), *args, **kwargs)
