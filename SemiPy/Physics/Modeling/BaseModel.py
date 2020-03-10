"""
This module contains the BaseModel class for all device physics models
"""


class BaseModel(object):

    def __init__(self, *args, **kwargs):
        pass

    def output(self, *args):
        raise NotImplementedError('You must implement the output function for the output of the model.')
