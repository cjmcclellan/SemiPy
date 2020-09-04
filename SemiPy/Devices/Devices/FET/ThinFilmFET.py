"""
Module for Thin Film Transistors (TFT)
"""
from SemiPy.Devices.Devices.FET.Transistor import NFET, PFET, FET, AmbipolarFET
from SemiPy.Devices.Materials.BaseMaterial import ThinFilm
from SemiPy.Devices.Materials.BaseMaterial import BaseMaterial


class TFT(FET):

    def __init__(self, substrate, *args, **kwargs):
        # run the super init
        super(TFT, self).__init__(*args, **kwargs)

        # now assert the channel is a thin film material
        assert isinstance(self.channel, ThinFilm), 'The channel for a TFT must be a thin film, not {0}'.format(type(self.channel))

        assert isinstance(substrate, BaseMaterial), 'The substrate must be a BaseMaterial, not {0}'.format(type(substrate))
        self.substrate = substrate


class pTFT(PFET, TFT):
    pass


class nTFT(NFET, TFT):
    pass


class ambiTFT(AmbipolarFET, TFT):
    NFET_Class = nTFT
    PFET_Class = pTFT
