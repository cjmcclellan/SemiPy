"""
This module contains the BaseInterface class for all Material Interfaces
"""
import SemiPy.Devices.Materials.Properties.Bulk.Electrical as mpbe
from SemiPy.Physics.DevicePhysics import compute_cox
from physics.fundamental_constants import free_space_permittivity_F_div_cm
from physics.value import Value, ureg
from SemiPy.Devices.Materials.BaseMaterial import BaseMaterial


interface_registry = {}


class InterfaceSuperClass(object):

    material1 = None
    material2 = None


def interface_registry_name(mat1, mat2):
    return '{0}_{1}'.format(mat1, mat2)


def register_interface(target_class):
    # assert isinstance(target_class, InterfaceSuperClass)
    interface_registry[interface_registry_name(target_class.material1, target_class.material2)] = target_class


class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        # if cls is not BaseInterface:
        register_interface(cls)
        return cls


class BaseInterface(InterfaceSuperClass, metaclass=Meta):

    properties = []

    def __init__(self):
        assert isinstance(self.material1, BaseMaterial), 'The materials must be of type BaseMaterial'
        assert isinstance(self.material2, BaseMaterial), 'The materials must be of type BaseMaterial'


def import_interface(material1, material2):
    try:
        return interface_registry[interface_registry_name(material1.__class__, material2.__class__)]
    except KeyError:
        try:
            return interface_registry[interface_registry_name(material2.__class__, material1.__class__)]
        except KeyError:
            raise AttributeError('Could not find an interface for the materials {0} and {1}'.format(material1, material2))
