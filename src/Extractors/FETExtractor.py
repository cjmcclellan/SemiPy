"""
Extractor for extracting information of Field-Effect Transistors from IdVg and IdVd data sets
"""
from .Extractors import Extractor
from ..Datasets.IVDataset import IdVgDataSet, IdVdDataSet


class FETExtractor(Extractor):

    def __init__(self, device_polarity, idvd_path=None, idvg_path=None, *args, **kwargs):

        super(FETExtractor, self).__init__(*args, **kwargs)

        self.idvd = IdVdDataSet(data_path=idvd_path)
        self.idvg = IdVgDataSet(data_path=idvg_path)


        # add some simple checks on the data.  Make sure Ig is not too high, Is and Id are reasonably matched, etc.
        assert

