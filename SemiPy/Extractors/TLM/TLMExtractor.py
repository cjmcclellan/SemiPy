"""
Extractor for extracting information of from TLM data
"""
from SemiPy.Extractors.Extractors import Extractor
from SemiPy.Datasets.IVDataset import IdVgDataSet, IdVdDataSet
from SemiPy.Extractors.Transistor.FETExtractor import FETExtractor
from physics.value import Value, ureg
import os
import warnings
import numpy as np
from SemiPy.helper.plotting import create_scatter_plot


class TLMExtractor(Extractor):

    def __init__(self, lengths, widths, tox, epiox, device_polarity, vd_values=None, idvg_path=None, *args, **kwargs):
        """
        An extractor object for Field-Effect Transistors (FETs).  To get FET properties, IdVd, or IdVg data, use the FET, idvd, and idvg
        attributes.  Look at FET, IdVgDataSet, and IdVdDataSet classes for understanding how to use these attributes.
        Args:
            length (Value or float):  Physical length of the FET.  Should be a Value with correct units or float in micrometers.
            width (Value or float): Physical length of the FET.  Should be a Value with correct units or float in micrometers.
            tox (Value or float): Physical thickness of the FET oxide.  Should be a Value with correct units or float in nanometers.
            epiox (Value or float): Dielectric constant of the oxide.  Should be a Value or float (unitless).
            device_polarity (str): The polarity of the device, either 'n' or 'p' for elector or hole, respectively.
            idvg_path (str): Path to the folder with all the IdVg data.
            *args:
            **kwargs:
        """

        # now create FETExtractors for every set of IdVg data
        self.FETs = []
        self.n = []
        self.r = []

        for root, dirs, idvg_data in os.walk(idvg_path):
            for idvg in idvg_data:
                path = os.path.join(root, idvg)
                self.FETs.append(FETExtractor(width=widths, length=lengths, epiox=epiox, tox=tox,
                                              device_polarity=device_polarity, idvg_path=path,
                                              vd_values=vd_values))

                # grab the n and resistances
                self.n.append(self.FETs[-1].idvg.get_column('n'))
                self.r.append(self.FETs[-1].idvg.get_column('resistance'))
        a = 5