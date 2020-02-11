"""
Base class for DataSets
"""
import os
import pandas as pd
import numpy as np


class BaseDataSet(object):

    def __init__(self, data_path):
        """
        Base class for all DataSets
        Args:
            data_path (str): Path to the csv, xls, or txt file
        """
        assert isinstance(data_path, str), 'The datapth must of type string'
        assert os.path.exists(data_path), 'The datapath you gave {0} does not exist'.format(data_path)

        self.data_path = data_path

        # now read the data.  If not txt, csv, or xls, raise and error
        if 'csv' in self.data_path:
            self.df = pd.read_csv(self.data_path)

        elif 'txt' in self.data_path:
            self.df = pd.read_csv(self.data_path, encoding='utf-16', sep='\t')

        elif 'xls' in self.data_path:
            self.df = pd.read_excel(self.data_path)

        else:
            raise ValueError('The file in data_path is not txt, csv, or xls.  Please change to the correct format')

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
