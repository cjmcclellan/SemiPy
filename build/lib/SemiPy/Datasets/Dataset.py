"""
Base class for DataSets
"""
import os
import pandas as pd
import numpy as np
import warnings
from SemiPy.helper.plotting import create_scatter_plot
from SemiPy.helper.wordsimilarity import levenshtein
from collections import OrderedDict


class BaseDataSet(object):

    master_independent = None

    master_dependent = None

    column_names = []

    def __init__(self, data_path, given_column_names, common_column_names):
        """
        Base class for all DataSets
        Args:
            data_path (str or pd.DataFrame): Path to the csv, xls, or txt file or just the actual DataFrame
        """
        self.data_path = data_path
        if isinstance(data_path, pd.DataFrame):
            self.df = data_path

        elif isinstance(data_path, dict):
            self.df = pd.DataFrame(data_path, dtype=np.object)
        else:
            assert isinstance(data_path, str), 'The datapth must of type string'
            assert os.path.exists(data_path), 'The datapath you gave {0} does not exist'.format(data_path)

            self.data_path = data_path

            # now read the data.  If not txt, csv, or xls, raise and error
            if 'csv' in self.data_path:
                self.df = pd.read_csv(self.data_path)

            elif 'txt' in self.data_path:
                try:
                    self.df = pd.read_csv(self.data_path, encoding='utf-16', sep='\t')
                except UnicodeError:
                    self.df = pd.read_csv(self.data_path, encoding='utf-8', sep='\t')

            elif 'xls' in self.data_path:
                self.df = pd.read_excel(self.data_path)

            else:
                raise ValueError('The file in data_path is not txt, csv, or xls.  Please change to the correct format')

        # placeholder for the gathered column names
        self.gathered_column_names = {}

        # loop th  rough all the column names
        for i in range(len(self.column_names)):
            # if no column name was given, then try to use common column names
            if given_column_names is None or given_column_names[i] is None:
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
        found_column = None
        for name in names:
            column_names = [col for col in self.df.columns if name.lower() in col.lower()]
            if len(column_names) != 0:
                if result is not None:
                    # if found two words, use the one that has the highest similarity
                    found = levenshtein(found_column, result[0])
                    new = levenshtein(name, column_names[0])
                    if found < new:
                        warnings.warn('Two of the names given correspond to columns in the table.  Using {0} for {1} instead of {2} for {3}'.format(result[0], found_column, column_names[0], name))
                        name = found_column
                        column_names = result
                    else:
                        warnings.warn(
                            'Two of the names given correspond to columns in the table.  Using {0} for {1} instead of {2} for {3}'.format(
                                column_names[0], name, result[0], found_column))
                # assert result is None, 'Two of the names given correspond to columns in the table'
                result = column_names
                found_column = name

        return result

    def add_column(self, column_name, column_data, column_major_name=None):
        """
        Add a column to the dataset
        Args:
            column_name (str): Name of the column to be added
            column_data (np.ndarray): ndarray of the column data to be added
            column_major_name (str): The name of the column major to be added to the gathered_column_names list, if not None
        Returns:
            None
        """
        assert isinstance(column_name, str), 'The column_name must be a string'
        assert isinstance(column_data, np.ndarray), 'The column_name must be an np.ndarray'
        assert column_name not in self.df.columns, 'The column_name {0} is already in the dataset'.format(column_name)

        try:
            self.df[column_name] = column_data
        except ValueError:
            # if value error, try to add the column data as a new dataframe
            additional = pd.DataFrame({column_name: column_data})
            self.df = pd.concat([self.df, additional], axis=1)

        # now add the column to the gathered columns list.
        if column_major_name is not None:
            if self.gathered_column_names.get(column_major_name, None) is None:
                self.gathered_column_names[column_major_name] = []
            # now add the new column
            self.gathered_column_names[column_major_name].append(column_name)

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

    def get_column(self, column_name, master_independent_value_range=None):
        """
        Get the column of the column_name
        Args:
            column_name (str): The name of the desired column.  Should be in the self.column_names list
            master_independent_value_range (list): Range of min and max values of the master independent to be indexed.  For each master
             independent column, values between the value closest to min and max will be indexed.  If min is 2.1 and the master independent
             is 1.0, 2.0, 3.0, the values greater than 2.0 will be indexed

        Returns:
            np.ndarray column data

        """
        column_name = column_name.lower()

        self.__assert_valid_column_name(column_name)

        result = self.df[self._get_column_names(column_name)].to_numpy()
        if master_independent_value_range is not None:
            master_column = self.df[self._get_column_names(self.master_independent)].to_numpy()
            # find the values in each column closest to the min and max values
            max_index = np.argmin(np.abs(master_column - np.ones(shape=(master_column.shape[-1],)) * master_independent_value_range[1]), axis=0)
            min_index = np.argmin(np.abs(master_column - np.ones(shape=(master_column.shape[-1],)) * master_independent_value_range[0]), axis=0)
            # now get the bool array
            # master_bool = np.logical_and(np.array(master_column, dtype=np.float) <= master_independent_value_range[1],
            #                              np.array(master_column, dtype=np.float) >= master_independent_value_range[0])
            # # now make sure the resulting array is square, otherwise raise an error
            dim = max_index[0] - min_index[0]
            # num_columns = master_bool.shape[1]
            # for i in range(master_bool.shape[-1]):
            temp_result = []
            for i in range(max_index.shape[0]):
                assert max_index[i] - min_index[i] == dim,\
                    "The indexing the column {0} by the master independent value range given {1} has resulted in a" \
                    " non rectangular array.  Make sure that all {2} master independent columns have the same number" \
                    " of data points for the given master independent value range".format(column_name,
                                                                                          master_independent_value_range,
                                                                                          self.master_independent)
                temp_result.append(result[min_index[i]:max_index[i], i])
            # now index the array

            # result = np.transpose(np.array([result[master_bool[:, i], i] for i in range(result.shape[-1])]))
            # result = np.transpose(np.reshape(result[master_bool], newshape=(num_columns, dim)))
            result = np.transpose(np.array(temp_result))
        return result

    def _get_column_names(self, column_name):
        # # first look if the column name is in the super gathered names list.
        # if column_name in self.super_gathered_column_names.keys():
        #     result = []
        #     for columns in self.super_gathered_column_names[column_name]:
        #         result = result + self.gathered_column_names[columns]
        #     return result
        if column_name in self.gathered_column_names.keys():
            return self.gathered_column_names[column_name]
        else:
            raise ValueError('Could not find the column {0} in the known columns'.format(column_name))

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
    def adjust_column_name(self, old_name, new_name):
        """
        Adjust the name of a column
        Args:
            old_name (str):
            new_name (str):

        Returns:

        """
        pass

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

        self.df[self._get_column_names(column_name)] = new_column

    def __assert_valid_column_name(self, column_name):
        assert column_name in self.gathered_column_names.keys(), 'The column name {0} is not in the list of column names {1}'.format(column_name,
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

    def get_master_indep_column(self):
        """
        Get the column data for the master independent variable
        Returns: np.ndarray

        """
        return self.get_column(self.master_independent)
    # def add_super_set(self, set_name, set_values):
    #     """
    #     Add a super set to the DataSet
    #     Args:
    #         set_name (str):
    #         set_values (list): List of set values
    #
    #     Returns:
    #         None
    #     """
    #     self.super_gathered_column_names[set_name] = set_values


class SetDataSet(BaseDataSet):

    secondary_independent = None

    def __init__(self, secondary_independent_values=None, *args, **kwargs):
        """
        A DataSet with sub sets within it dictated by the secondary_independent variable.  If there are any duplicate values for the
        secondary_independent, the first value will be used
        Args:
            *args:
            **kwargs:
        """

        super(SetDataSet, self).__init__(*args, **kwargs)

        if self.data_path is not None:
            # now gather what the secondary independent values are for each set
            if secondary_independent_values is None:
                assert self._get_column_names(self.secondary_independent) is not None,\
                    'Cannot find the required column {0} in the dataset'.format(self.secondary_independent)
                column_values = self.get_column(self.secondary_independent)[:, 0]
            else:
                num_sets = self.get_column(self.master_independent).shape[0]
                assert num_sets == len(secondary_independent_values),\
                    'You provided {0} values for {1}, but there are {2} sets'.format(len(secondary_independent_values),
                                                                                     self.secondary_independent, num_sets)
                column_values = secondary_independent_values

            self.secondary_indep_values = OrderedDict()

            # loop through grabbing the values and ignoring any duplicates (always taking the first column)
            index = 0
            for i in range(len(column_values)):
                if self.secondary_indep_values.get(column_values[i], None) is None and not np.isnan(column_values[i]):
                    # now add all the column names to the secondary_indep_values dict
                    self.secondary_indep_values[column_values[i]] =\
                        [column[index] for column in self.gathered_column_names.values() if column is not None]
                    index += 1
                # else remove all the data from that set
                else:
                    self.remove_column(column_name=[columns[index] for columns in self.gathered_column_names.values() if columns is not None])

            # count the number of sets
            self.num_secondary_indep_sets = len(self.secondary_indep_values.keys())

    def __assert_secondary_value(self, value):
        assert value in self.secondary_indep_values.keys(),\
            'The secondary value of {0} for {1} is not in the list of secondary values of this dataset {2}'.format(value,
                                                                                                                   self.secondary_independent,
                                                                                                                   list(self.secondary_indep_values.keys()))

    # def add_super_set(self, set_name, set_values):
    #     # same as DataSet, but adds the

    def get_column(self, column_name, return_set_values=False, master_independent_value_range=None):
        """

        Args:
            column_name:
            return_set_values (bool): If True, return the columns and corresponding set values

        Returns:
            np.ndarray
        """
        # same as super class, just make sure the shape is column, row not row, column
        column_data = np.transpose(super(SetDataSet, self).get_column(column_name, master_independent_value_range))
        if return_set_values:
            return column_data, list([key for key in self.secondary_indep_values.keys()
                                      if self.gathered_column_names[column_name]])
        return column_data

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

    def __get_column_name_secondary_value(self, column_name, secondary_value):

        self.__assert_secondary_value(secondary_value)
        secondary_column_names = self.secondary_indep_values[secondary_value]

        # get all the columns for that name
        column_names = self._get_column_names(column_name)

        # now return any overlapping names in the two lists
        return list(set(column_names).intersection(secondary_column_names))

    def get_set_indexed_columns(self, column_name):
        """
        Get a dictionary of columns with keys being the set values

        Args:
            column_name (str): The name of the desired column

        Returns:
            dict of columns with set values as keys
        """
        result = {}
        for set_value in self.secondary_indep_values.keys():
            result[set_value] = self.get_column_set(column_name, set_value)

        return result

    def get_column_set(self, column_name, secondary_value):
        """
        Similar to get_column but allows index by the secondary_value to return a single column
        Args:
            column_name (str): The name of the column wanted.  Should be in self.column_names
            secondary_value (int, float): The value of the secondary_independent to be indexed

        Returns:
            np.ndarray of the column
        """


        # get the index of that value

        # column_name = column_name.lower()

        # assert column_name in self.column_names, 'The column name {0} is not in the list of column names {1}'.format(column_name,
        #                                                                                                              self.column_names)
        # now return the column
        # column_names = self._get_column_names(column_name)
        # only grab columns from that set.
        columns = self.__get_column_name_secondary_value(column_name, secondary_value)
        result = self.df[columns].to_numpy()
        assert result.shape[1] == 1, 'You are attempting to grab multiple columns for a single secondary_value, which should not be' \
                                     ' possible.  You have found a bug, congrats.  Please report'
        return result[:, 0]

    def __assert_valid_column(self, column_name, column_data):
        """
        Asserts the column_name and data are valid for this DataSet
        Args:
            column_name:
            column_data (np.ndarray):

        Returns:self._get_column_names(column_name)

        """
        assert isinstance(column_data, np.ndarray), 'The column_data must be of type np.ndarray, not {0}'.format(type(column_data))
        # assert column_data.shape[0] == len(self.secondary_indep_values.keys())

    def add_column(self, column_name, column_data, secondary_indep_value=None):
        """
        Similar to DatSet.add_column but enforces that there must enough columns for every subset ofvd_values=None,  the dataset
        Args:
            column_name (str):
            column_data (np.ndarray): The committing data.  Should be of shape (number of subsets, number of rows)
            secondary_indep_value (float): The value of the secondary independent.  If None, then just add as normal
        Returns:
            None
        """
        self.__assert_valid_column(column_name, column_data)

        if secondary_indep_value is not None:
            self.__assert_secondary_value(secondary_indep_value)
            new_column_name = '{0}_{1}'.format(column_name, secondary_indep_value)
            self.secondary_indep_values[secondary_indep_value].append(new_column_name)
            super(SetDataSet, self).add_column(new_column_name, column_data, column_major_name=column_name)

        # now add each new column to the dataset
        else:
            for i, key in enumerate(self.secondary_indep_values.keys()):
                new_column_name = '{0}_{1}'.format(column_name, i)
                self.secondary_indep_values[key].append(new_column_name)
                super(SetDataSet, self).add_column(new_column_name, column_data[i, :], column_major_name=column_name)

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

    def get_secondary_indep_values(self):
        """
        Get a list of the secondary independent values
        Returns:
            list
        """
        return list(self.secondary_indep_values.keys())

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
