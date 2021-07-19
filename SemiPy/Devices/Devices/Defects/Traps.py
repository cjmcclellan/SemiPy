"""
Module for electrical Traps.
"""


class Trap(object):

    """
    An electrical trap in a transistor
    Args:
        Eit: The energy level of the trap with respect to the nearest energy band
        Dit: The density of the traps
        ntype: The type of trap. If true, the trap is ntype, if false the trap is ptype
    """
    def __init__(self, Eit, Dit, ntype=True):

        # save the Eit and Dit
        self.Eit = Eit
        self.Dit = Dit

        # save the trap type
        self.type = 'ntype' if ntype else 'ptype'

