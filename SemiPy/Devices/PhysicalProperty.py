"""
This module holds the base class for Physical Properties
"""
from physics.units import ureg
from physics.value import Value, MetaValue
from physics.helper import assert_value
from SemiPy.Documentation.ScientificPaper import ScientificPaper


class PhysicalProperty(MetaValue):

    prop_name = None
    prop_dimensionality = None
    # the value will be adjusted to the standard units and rounded to two decimal places
    prop_standard_units = None

    citations = []

    input_value_names = []
    input_dimensionalities = []

    optional_input_value_names = []
    optional_input_dimensionalities = []

    def __init__(self, cited=False, value=None, name=None, input_values=None, citation=None):
        """
        PhysicalProperty records a specific physical property of a SemiPy object, such as the thermal conductivity of
        Silicon or mobility extracted from a MoS2 FET.  PhysicalProperties ensure correct dimensionality and also record
        the conditions of the property as input_values, such as the temperature of the thermal conductivity measurement
        or carrier density of the device mobility.  PhysicalProperties can also be used in math operations just as Values
        are.

        There are two types of PhysicalProperties, extracted and cited.  Extracted are properties extracted from data
        by the user and cited are from scientific publications.  Cited PhysicalProperties should be defined for given
        Materials, not during code execution.  Extracted PhysicalProperties should be recorded by the user in their
        specific code as they are only relevant to that user.
        """
        self.value = None
        self.input_values = {}
        # save the name of the property
        if name is None:
            self.name = self.prop_name
        else:
            assert isinstance(name, str), 'The given name of the property must be a string'
            self.name = name
        # save the type of PhysicalProperty
        self.cited = cited
        # self.extracted = extracted
        # assert self.cited ^ self.extracted, 'The PhysicalProperty {0} must be either cited or extracted' \
        #                                     ' type. You gave {1}'.format(self.prop_name,
        #                                                                  'both' if self.cited and self.extracted
        #                                                                  else 'neither')
        if self.cited:
            assert value is not None, 'You must give the value for a cited PhysicalProperty.'
            assert citation is not None, 'You must give a citation for a cited PhysicalProperty.'
            assert isinstance(citation, ScientificPaper), 'Your citation must be of type ScientificPaper, not {0}'.format(type(citation))
            self.citations.append(citation)
        if value is not None:
            self.set(value, input_values)

    def __getitem__(self, item):
        """
        Get any item of this property
        Args:
            item (str):

        Returns:
            Value
        """
        if item == self.prop_name:
            return self.value
        elif item in self.input_value_names or item in self.optional_input_value_names:
            return self.input_values[item]
        else:
            raise ValueError('The item {0} is not a part of this device property.'.format(item))

    # def __get__(self, instance, owner):
    #     return self.value

    # def __set__(self, instance, value):
    #     assert_value(value)
    #     assert value.unit.dimensionality == self.prop_dimensionality.dimensionality,\
    #         'Your dimensionality is incorrect for {0}. Yours is {1}, but it should be {2}'.format(self.prop_name,
    #                                                                                               value.unit.dimensionality,
    #                                                                                               self.prop_dimensionality.dimensionality)
    #     self.value = value

    def set(self, value, input_values=None):
        """
        Set the property and input values for this Device Property.
        Args:
            value (physics.Value): The Value to be set for this property
            input_values (dict): A dictionary of the input values, using the convention {'input_name': input_value}

        Returns:
            None
        """
        # save the prop value
        assert_value(value)
        assert value.unit.dimensionality == self.prop_dimensionality.dimensionality, 'Your dimensionality is incorrect for {0}. Yours is {1}, but it should be' \
                ' {2}'.format(self.prop_name, value.unit.dimensionality, self.prop_dimensionality.dimensionality)
        self.value = value

        # now if the standard units were given, then adjust the value units
        if self.prop_standard_units is not None:
            self.value = self.value.adjust_unit(self.prop_standard_units)
            # now round the value to 2 decimal places
            self.value = Value(value=round(self.value.magnitude * 100) / 100, unit=self.value.unit)

        # save the input values, making sure that they match the given names
        for i, input_name in enumerate(self.input_value_names):
            assert input_values is not None, 'You are missing the required {0} input for the {1} property'.format(input_name, self.prop_name)
            input_value = input_values.get(input_name, None)
            assert input_value is not None, 'You are missing the required {0} input for the {1} property'.format(input_name, self.prop_name)
            assert_value(input_value)
            assert input_value.unit.dimensionality == self.input_dimensionalities[i].dimensionality,\
                'Your dimensionality is incorrect for input {0}.  Yours is {1}, but it should be' \
                ' {2}'.format(input_name, input_value.unit.dimensionality, self.input_dimensionalities[i].dimensionality)

            self.input_values[input_name] = input_value

        # now go through the optional input values if there a given input values
        if input_values is not None:
            for i, optional_name in enumerate(self.optional_input_value_names):
                input_value = input_values.get(optional_name, None)
                if input_value is not None:
                    assert_value(input_value)
                    assert input_value.unit.dimensionality == self.input_dimensionalities[i].dimensionality, \
                        'Your dimensionality is incorrect for input {0}.  Yours is {1}, but it should be' \
                        ' {2}'.format(optional_name, input_value.unit.dimensionality, self.input_dimensionalities[i].dimensionality)

                    self.input_values[optional_name] = input_value

    def __str__(self):
        return '{0} = {1}'.format(self.name, self.value)


class CustomPhysicalProperty(PhysicalProperty):

    def __init__(self, name, dimensionality, *args, **kwargs):

        self.prop_name = name
        self.prop_dimensionality = dimensionality

        super(CustomPhysicalProperty, self).__init__(*args, **kwargs)
