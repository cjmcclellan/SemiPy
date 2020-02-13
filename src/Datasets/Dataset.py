"""
Base class for DataSets
"""
import os
import pandas as pd
import numpy as np
import warnings
from ..helper.plotting import create_scatter_plot


class BaseDataSet(object):

    master_independent = None

    master_dependent = None

    column_names = []

    def __init__(self, data_path, given_column_names, common_column_names):
        """
        Base class for all DataSets
        Args:
            data_path (str): Path to the csv, xls, or txt file.
        """
        assert isinstance(data_path, str), 'The datapth must of type string'
        assert os.path.exists(data_path), 'The datapath you gave {0} does not exist'.format(data_path)

        self.data_path = data_path

        # placeholder for the gathered column names
        self.gathered_column_names = {}

        # now read the data.  If not txt, csv, or xls, raise and error
        if 'csv' in self.data_path:
            self.df = pd.read_csv(self.data_path)

        elif 'txt' in self.data_path:
            self.df = pd.read_csv(self.data_path, encoding='utf-16', sep='\t')

        elif 'xls' in self.data_path:
            self.df = pd.read_excel(self.data_path)

        else:
            raise ValueError('The file in data_path is not txt, csv, or xls.  Please change to the correct format')

        # loop th  rough all the column names
        for i in range(len(self.column_names)):
            # if no column name was given, then try to use common column names
            if given_column_names[i] is None:
                names = self._find_similar_column(common_column_names[i])
            else:
                names = self._find_similar_column(given_column_names[i])

            if names is None:
                assert not (self.column_names[i] is self.master_dependent or self.column_names[i] is self.master_independent),\
                    'Cannot find the column for {0}'.format(self.column_names[i])
                warnings.warn('Cannot find the column for {0} in the data set'.format(self.column_names[i]))

            self.gathered_column_names[self.column_names[i]] = names

    def _find_similar_column(self, names):
        """
        Try to find the columns that closely match the names
        Args:
            names (list or str): List of strings or a single string of the column(s) trying to be found

        Returns:
            name of the columns

        """
        result = None
        # if a string, make it into a list
        if isinstance(names, str):
            names = [names]

        # loop through looking for subset names.  If two names work, then raise an error.  This could be adjusted later that it defaults
        # to the longer name
        for name in names:
            column_names = [col for col in self.df.columns if name.lower() in col.lower()]
            if len(column_names) != 0:
                assert result is None, 'Two of the names given correspond to columns in the table'
                result = column_names

        return result

    def add_column(self, column_name, column_data):
        """
        Add a column to the dataset
        Args:
            column_name (str): Name of the column to be added
            column_data (np.ndarray): ndarray of the column data to be added

        Returns:
            None
        """
        assert isinstance(column_name, str), 'The column_name must be a string'
        assert isinstance(column_data, np.ndarray), 'The column_name must be an np.ndarray'
        assert column_name not in self.df.columns, 'The column_name {0} is already in the dataset'.format(column_name)

        self.df[column_name] = column_data

    def remove_column(self, column_name):
        """
        Remove a column from the DataSet
        Args:
            column_name (str or list): The name of the column to be removed.

        Returns:
            None
        """
        self.df.drop(labels=column_name, axis=1)
        # now remove from the gathered_column_names
        if isinstance(column_name, list):
            for name in column_name:
                for key, columns in self.gathered_column_names.items():
                    if columns is not None and name in columns:
                        columns.remove(name)
                        self.gathered_column_names[key] = columns
        else:
            for key, columns in self.gathered_column_names.items():
                if columns is not None and column_name in columns:
                    columns.remove(column_name)
                    self.gathered_column_names[key] = columns

    def get_column(self, column_name):
        """
        Get the column of the column_name
        Args:
            column_name (str): The name of the desired column.  Should be in the self.column_names list

        Returns:
            np.ndarray column data
        """
        column_name = column_name.lower()

        self.__assert_valid_column_name(column_name)

        return self.df[self.gathered_column_names[column_name]].to_numpy()

    # def update_column(self, column_name, data):
    #     """
    #     Update the data in a column
    #     Args:
    #         column_name (str): The name of the column to be adjusted
    #         data (np.array): A 1D np array with the new data
    #
    #     Returns:
    #         None
    #     """
    #

    def adjust_column(self, column_name, func):
        """
        Adjust a column using a lambda function
        Args:
            column_name (str): The name of the column to be adjusted
            func (lambda):  The lambda function that will adjust the column

        Returns:
            None
        """
        new_column = func(self.get_column(column_name))

        self.df[self.gathered_column_names[column_name]] = new_column

    def __assert_valid_column_name(self, column_name):
        assert column_name in self.column_names, 'The column name {0} is not in the list of column names {1}'.format(column_name,
                                                                                                                     self.column_names)

    def create_scatter_plot(self, x_column, y_column, scale='lin', autoscale=True):
        """
        Creates and plots a scatter plot of data in the dataset.
        Args:
            x_column (str): Column name of the x_data
            y_column (str): Column name of the y_data
            scale (str): The desired scale of the y_axis (either 'log' or 'lin')
            autoscale (bool): Flag for autoscaling the data

        Returns:
            None.  Just plots the plot
        """
        create_scatter_plot(x_data=self.get_column(x_column), y_data=self.get_column(y_column), scale=scale, autoscale=autoscale)


class SetDataSet(BaseDataSet):

    secondary_independent = None

    def __init__(self, *args, **kwargs):
        """
        A DataSet with sub sets within it dictated by the secondary_independent variable.  If there are any duplicate values for the
        secondary_independent, the first value will be used
        Args:
            *args:
            **kwargs:
        """

        super(SetDataSet, self).__init__(*args, **kwargs)

        # now gather what the secondary independent values are for each set
        column_values = self.get_column(self.secondary_independent)

        self.secondary_indep_values = {}

        # loop through grabbing the values and ignoring any duplicates (always taking the first column)
        index = 0
        for i in range(len(self.gathered_column_names[self.secondary_independent])):
            if self.secondary_indep_values.get(column_values[i][0], None) is None and not np.isnan(column_values[i][0]):
                self.secondary_indep_values[column_values[i][0]] = index
                index += 1
            # else remove all the data from that set
            else:
                self.remove_column(column_name=[columns[index] for columns in self.gathered_column_names.values() if columns is not None])

    def __assert_secondary_value(self, value):
        assert value in self.secondary_indep_values.keys(),\
            'The secondary value of {0} for {1} is not in the list of secondary values of this dataset {2}'.format(value,
                                                                                                                   self.secondary_independent,
                                                                                                                   list(self.secondary_indep_values.keys()))

    def get_column(self, column_name):
        # same as super class, just make sure the shape is column, row not row, column
        return np.transpose(super(SetDataSet, self).get_column(column_name))

    def adjust_column(self, column_name, func):
        """
        Similar to adjust_column for DataSet but deals with 2D arrays
        Args:
            column_name:
            func:

        Returns:
            None
        """
        new_column_data = func(self.get_column(column_name))
        # run the update func on every row individually
        # for i in range(new_column_data.shape[0]):
        #     new_column_data[i] = func(new_column_data[i])

        # now update the rows
        self.update_column_data(column_name, new_column_data)

        # for key, i in self.secondary_indep_values.items():
        #     # new_column_name = '{0}_{1}'.format(column_name, i)
        #     super(SetDataSet, self).adjust_column(self.gathered_column_names, column_data[i, :])

    def get_column_set(self, column_name, secondary_value):
        """
        Similar to get_column but allows index by the secondary_value to return a single column
        Args:
            column_name (str): The name of the column wanted.  Should be in self.column_names
            secondary_value (int, float): The value of the secondary_independent to be indexed

        Returns:
            np.ndarray of the column
        """

        self.__assert_secondary_value(secondary_value)

        # get the index of that value
        i = self.secondary_indep_values[secondary_value]

        column_name = column_name.lower()

        assert column_name in self.column_names, 'The column name {0} is not in the list of column names {1}'.format(column_name,
                                                                                                                     self.column_names)
        # now return the column
        return self.df[self.gathered_column_names[column_name][i]].to_numpy()

    def __assert_valid_column(self, column_name, column_data):
        """
        Asserts the column_name and data are valid for this DataSet
        Args:
            column_name:
            column_data (np.ndarray):

        Returns:

        """
        assert isinstance(column_data, np.ndarray), 'The column_data must be of type np.ndarray, not {0}'.format(type(column_data))
        assert column_data.shape[0] == len(self.secondary_indep_values.keys())

    def add_column(self, column_name, column_data):
        """
        Similar to DatSet.add_column but enforces that there must enough columns for every subset of the dataset
        Args:
            column_name (str):
            column_data (np.ndarray): The committing data.  Should be of shape (number of subsets, number of rows)

        Returns:
            None
        """
        self.__assert_valid_column(column_name, column_data)

        # now add each new column to the dataset
        for key, i in self.secondary_indep_values.items():
            new_column_name = '{0}_{1}'.format(column_name, i)
            super(SetDataSet, self).add_column(new_column_name, column_data[i, :])

    def update_column_data(self, column_name, column_data):
        """
        Update the data in a column
        Args:
            column_name (str): The name of the column
            column_data (np.ndarray): The column data array.  Should be 2D

        Returns:
            None
        """
        self.__assert_valid_column(column_name, column_data)

        # now loop through the rows in column_data and adjust the columns
        for i, row in enumerate(column_data):
            self.df[self.gathered_column_names[column_name][i]] = row

    def add_column_set(self, column_name, column_data, secondary_value):
        """
        Similar to add_column, but allows adding a column specifically to a set indexed by the secondary value a column to the dataset
        Args:
            column_name (str): Name of the column to be added
            column_data (np.ndarray): ndarray of the column data to be added
            secondary_value (int or float): The value of the secondary_independent to be indexed

        Returns:
            None
        """
        assert isinstance(column_name, str), 'The column_name must be a string'
        assert isinstance(column_data, np.ndarray), 'The column_name must be an np.ndarray'
        self.__assert_secondary_value(secondary_value)
        assert column_name not in self.df.columns, 'The column_name {0} is already in the dataset'.format(column_name)

        raise NotImplementedError('Need to finish')

        self.df[column_name] = column_data
