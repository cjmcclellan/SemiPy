"""
Basic plot class
"""
import matplotlib.pyplot as plt
from physics.value import Value, ureg, pint_to_str
import os


class BasicPlot(object):

    x_axis_title = ''
    x_axis_scale = 'linear'
    x_units = None

    y_axis_title = ''
    y_axis_scale = 'linear'
    y_units = None

    def __init__(self, name, x_units=None, y_units=None, *args, **kwargs):

        # save the name
        self.name = name

        # save the units
        if x_units is not None:
            self.x_units = x_units
        if y_units is not None:
            self.y_units = y_units

        # create the Figure
        self.fig = plt.figure(*args, **kwargs)

    def add_data(self, x_data, y_data, *args, **kwargs):

        # update the units from the data
        if isinstance(x_data[0], Value):
            self._adjust_value_array_units(x_data, self.x_units)
        else:
            self.x_units = None

        if isinstance(y_data[0], Value):
            self._adjust_value_array_units(y_data, self.y_units)
        else:
            self.y_units = None

        # add the data to the plot
        plt.plot(x_data, y_data, *args, **kwargs)

    @staticmethod
    def _adjust_value_array_units(array, new_unit):
        assert array[0].unit.dimensionality == new_unit.dimensionality, 'The dimensionality of the array and new unit do not match.'
        for i, v in enumerate(array):
            array[i] = array[i].adjust_unit(new_unit)

    def _finalize_plot(self):
        plt.xlabel(self._add_unit_to_title(self.x_axis_title, self.x_units))
        plt.xscale(self.x_axis_scale)
        plt.ylabel(self._add_unit_to_title(self.y_axis_title, self.y_units))
        plt.yscale(self.y_axis_scale)

    @staticmethod
    def _add_unit_to_title(title, unit):
        if unit is not None:
            return title + ' ({0})'.format(pint_to_str(unit))
        else:
            return title

    def show_plot(self):
        self._finalize_plot()
        plt.show()

    def save(self, path=None):

        self._finalize_plot()
        if path is None:
            path = self.name
        else:
            path = os.path.join(path, self.name)

        # now save the figure
        self.fig.savefig(path + '.png')
