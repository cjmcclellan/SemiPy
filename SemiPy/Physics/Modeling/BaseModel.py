"""
This module contains the BaseModel class for all device physics models
"""
from SemiPy.Documentation.ScientificPaper import ScientificPaper


class BaseModel(object):

    # citations for the model
    citations = []

    def __init__(self, *args, **kwargs):
        assert len(self.citations) != 0, 'You must give citations for this model.'
        assert all([isinstance(citation, ScientificPaper) for citation in self.citations]), 'All citations must be of type ScientificPaper'

    def output(self, *args):
        raise NotImplementedError('You must implement the output function for the output of the model.')
