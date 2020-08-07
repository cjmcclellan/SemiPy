"""
Basic Plotting object
"""
import plotly.graph_objects as go
import numpy as np


class BasePlotlyPlot(object):

    def __init__(self, *args, **kwargs):

        self.fig = go.Figure()

    @staticmethod
    def _check_array(array):
        array = np.array(array)
        assert len(array.shape) == 2 or len(array.shape) == 1, 'The array data you gave is off.  It has a dimension of {0} but should ' \
                                                               'only have a dimension of 1 or 2'.format(len(array.shape))
        return array


class Base2DPlot(BasePlotlyPlot):

    def __init__(self, x_data, y_data, classes=None, *args, **kwargs):
        """

        Args:
            x_data (np.ndarray): X data of the plot. Should have 1 or 2 dimensions.  If 2 dimensions, the classes should be the 2nd dimension
            y_data (np.ndarray): Y data of the plot. Should have same shape as x_data.
            classes (None or np.ndarray): The class labels of the data. Either None or np.ndarray with 1 dimension and shape equal to x_data.shape[0]
            *args:
            **kwargs:
        """
        super(Base2DPlot, self).__init__(args, kwargs)

        self.x_data, self.y_data, self.classes = self.__check_shapes(x_data, y_data, classes)

        # now add to the

    def __check_shapes(self, x_data, y_data, classes):
        # check arrays
        x_data = self._check_array(x_data)
        y_data = self._check_array(y_data)
        assert x_data.shape == y_data.shape, 'The x_data shape {0} is not the same as the y_data shape {1}'.format(x_data.shape,
                                                                                                                   y_data.shape)
        if classes is not None:
            classes = self._check_array(classes)
            assert classes.shape[0] == x_data.shape[1], 'The classes shape {0} and data shapes {1} are off. Make sure the classes shape ' \
                                                        'equals the 2nd dimension of x and y_data'.format(classes.shape, x_data.shape)
            assert len(classes.shape) == 1, 'The classes dimension is off.  It is {0} but should be 1'.format(len(classes.shape))

        return x_data, y_data, classes



class Base3DPlot(object):

    def __init__(self, x_data, y_data, z_data):
        pass
