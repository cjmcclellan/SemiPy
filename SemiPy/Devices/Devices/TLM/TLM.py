"""
Module for Transfer Length Method (TLM) device structures.
"""
from SemiPy.Devices.Devices.BaseDevice import BaseDevice, Voltage


class TLM(BaseDevice):

    fets = {}

    def __init__(self, *args, **kwargs):

        super(TLM, self).__init__(*args, **kwargs)

