"""
Base classes for Datasets.  The methodoligy for datasets should be give a text, csv, or xls file and the dataset will
import and track all columns.
"""


class DataSet(object):


    def __init__(self, data_path, pd_dataset=None):

        # if a dataset is given, then use that.  Otherwise, import that data
        if pd_dataset is not None:
            self.data = pd_dataset
        else:
            assert isinstance(data_path, str), 'The datapth must of type string'
            assert os.path.exists(data_path), 'The datapath you gave {0} does not exist'.format(data_path)

            self.data_path = data_path

            # now read the data.  If not txt, csv, or xls, raise and error
            if 'csv' in self.data_path:
                self.data = pd.read_csv(self.data_path)

            elif 'txt' in self.data_path:
                try:
                    self.date = pd.read_csv(self.data_path, encoding='utf-16', sep='\t')
                except UnicodeError:
                    self.data = pd.read_csv(self.data_path, encoding='utf-8', sep='\t')

            elif 'xls' in self.data_path:
                self.data = pd.read_excel(self.data_path)

            else:
                raise ValueError('The file in data_path is not txt, csv, or xls.  Please change to the correct format')



