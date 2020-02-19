"""
This will house some basic device physics equations
"""
import numpy as np
from physics.fundamental_constants import free_space_permittivity_F_div_cm, electron_charge_C
# from physics.helper import assert_value
from physics.units import ureg
# from physics.value import Value


def compute_mobility(gm, cox, vd, l, w=None):
    result = gm * l / (cox * vd)
    if w is None:
        return result / w
    else:
        return result


def compute_cox(dielectric_constant, tox):
    return (free_space_permittivity_F_div_cm * dielectric_constant / tox).adjust_unit(ureg.farad / (ureg.centimeter ** 2))


def carrier_density(cox, vg, vt):
    return cox * (vg - vt) / electron_charge_C
