"""
Extractor objects for processing data
"""
import numpy as np
import matplotlib.pyplot as plt
from physics.value import Value


class Extractor(object):

    def __init__(self, *args, **kwargs):
        """
        Base class for data extractors
        Args:
            data_path (str): Path to the datafile
        """
        self.x_data = None
        self.y_data = None

    def _clean_data(self, ndarry):
        """
        Remove all nan and inf from an ndarray by replacing with 0.0
        Args:
            ndarry (np.ndarray): The ndarray to be cleaned

        Returns:
            The cleaned ndarray
        """
        ndarry[ndarry == np.inf] = 0.0
        ndarry[ndarry == -np.inf] = 0.0
        ndarry = np.nan_to_num(ndarry)
        return ndarry

    def _slope(self, x_data, y_data, keep_dims=False):
        """
        Compute the slope at all data points
        Args:
            x_data (np.array): The x data of size n
            y_data (np.array): The y data of size n
            keep_dims (bool): If true, result will have size n

        Returns:
            ndarray: The slope at all points (size n - 1 or n if keep_dims is True)

        """
        slope = np.diff(y_data)/np.diff(x_data)
        if keep_dims:
            slope = np.concatenate((slope, slope[..., -1:]), axis=-1)
        return self._clean_data(slope)

    def _plot_line(self, x_min, x_max, a, b):
        x_data = Value.array_like(array=np.linspace(x_min, x_max), unit=x_min.unit)
        y_data = x_data*a + b
        plt.plot(x_data, y_data)

    def _linear_extraction(self, x, y, slope=None, y_inter=None, x_inter=None):
        """
        Creates a line from a x and y point and either the slope, y intercept, or x intercept
        Args:
            x (float): The x data point
            y (float): The y data point
            slope (float): The slope
            y_inter (float): The y intercept value
            x_inter (float): The x intercept value

        Returns:
            (a, b, x_inter): The a and b in y = ax + b and the x intercept
        """
        if slope is not None:
            b = y - slope * x
            a = slope
            x_inter = -1*b/a
        elif y_inter is not None:
            a = (y - y_inter)/x
            b = y_inter
            x_inter = -1*b/a
        elif x_inter is not None:
            a = y / (x - x_inter)
            b = y - a * x
        else:
            raise ValueError('You did not give a slope, y_inter, or x_inter.')

        return a, b, x_inter

    def extract_data(self):
        raise NotImplementedError('You must implement the extract_data function for the Extractor')


class TrendLine(object):

    def __init__(self, x_data, y_data, trend_area):
        # self.fit, error = np.polyfit(np.log10(x_data), np.log10(y_data), 2, cov=True)
        self.fit_data(x_data, y_data)
        # self.x_trend = np.logspace(np.log10(x_data.min()), np.log10(x_data.max()), num=100)
        # x_log = np.log10(self.x_trend)
        # # y_trend = np.exp([fit[0]*x**1 + fit[1]*x**0 for x in x_log])
        # self.y_trend = np.power([10 for x in x_log], [self.compute_fit(x) for x in x_log])

        # now just get the fit within trend_area * y_area
        # y_error = 2*trend_area #error[1][1]

        # x_data_new = []
        # y_data_new = []
        # for y, x in zip(y_data, x_data):
        #     y_fit = np.log10(self.compute_fit(x))
        #     if (y_fit - y_error < np.log10(y)) and (y_fit + y_error > np.log10(y)):
        #         x_data_new.append(x)
        #         y_data_new.append(y)
        #
        # self.fit_data(np.array(x_data_new), np.array(y_data_new))

        # y_trend = np.exp([fit[0]*x_log[0]**2 + fit[1]*x_log[0]**1 + fit[2]*x_log[0]**0,
        #            fit[0] * x_log[1] ** 2 + fit[1] * x_log[1] ** 1 + fit[2] * x_log[1] ** 0])
        # x_inter = -fit[1]/fit[0]

    def compute_fit(self, x):
        x = np.log10(x)
        return 10**(self.fit[0] * x ** 2 + self.fit[1] * x ** 1 + self.fit[2])

    def get_x_y(self):
        return self.x_trend, self.y_trend

    def fit_data(self, x_data, y_data):
        self.fit, self.error = np.polyfit(np.log10(x_data), np.log10(y_data), 2, cov=True)

        self.x_trend = np.logspace(np.log10(x_data.min()), np.log10(x_data.max()), num=100)
        # x_log = np.log10(self.x_trend)
        # y_trend = np.exp([fit[0]*x**1 + fit[1]*x**0 for x in x_log])
        self.y_trend = self.compute_fit(self.x_trend)
        # self.y_trend = np.power([10 for x in self.x_trend], [self.compute_fit(x) for x in self.x_trend])
