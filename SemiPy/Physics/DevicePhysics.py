"""
This will house some basic device physics equations
"""
import numpy as np
from physics.fundamental_constants import free_space_permittivity_F_div_cm, electron_charge_C
# from physics.helper import assert_value
import math
from physics.value import Value, ureg


def units_decorator(citation):
    def dec(obj):
        obj.__doc__ = obj.__doc__.replace('<citation>', citation.doc_string_ref())
        return obj
    return dec


def compute_mobility(gm, cox, vd, l, w=None):
    result = gm * l / (cox * vd)
    if w is None:
        return result / w
    else:
        return result


def compute_sheet_resistance(carrier_density, mobility):
    return 1 / (carrier_density * mobility * electron_charge_C)


def compute_cox(dielectric_constant, tox):
    return (free_space_permittivity_F_div_cm * dielectric_constant / tox).adjust_unit(ureg.farad / (ureg.centimeter ** 2))


def carrier_density(cox, vg, vt):
    return Value(value=1.0, unit=ureg.coulomb) * cox * (vg - vt) / (electron_charge_C * Value(value=1.0, unit=ureg.volt * ureg.farad))


def characteristic_length(epichannel, epiox, tchannel, tox):
    """
    Compute the characteristic length of a FET (lambda = sqrt(epi_channel * t_channel * tox / epi_ox))
    Args:
        epichannel:
        epiox:
        tchannel:
        tox:

    Returns:
        lambda
    """
    return math.sqrt(epichannel * tchannel * tox / epiox)
