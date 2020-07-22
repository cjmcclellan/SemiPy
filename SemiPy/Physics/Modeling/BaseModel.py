"""
This module contains the BaseModel class for all device physics models
"""
from SemiPy.Documentation.ScientificPaper import ScientificPaper
import numpy as np
from physics.value import Value


class BaseModel(object):

    # citations for the model
    citations = []

    required_inputs = []

    def __init__(self, *args, **kwargs):
        try:
            assert len(self.citations) != 0, 'You must give citations for this model.'
            assert all([isinstance(citation, ScientificPaper) for citation in self.citations]), 'All citations must be of type ScientificPaper'
        except AssertionError:
            print('Warning, you should add citations to the model')

    def model_output(self, *args):
        raise NotImplementedError('You must implement the output function for the output of the model.')


class ModelInput(object):
    """
    Model input class for making inputs to physics models.  Defaults to num if given.
    Args:
        min (float or int):
        max (float or int):
        num (int):
        step (float or int):
    """

    def __init__(self, min, max, unit, num=None, step=None):

        assert num is not None or step is not None, 'You must give a step or num value'

        if num is not None:
            self.range = np.linspace(min, max, num)

        elif step is not None:
            self.range = np.arange(min, max, step)

        self.range = Value.array_like(self.range, unit=unit)