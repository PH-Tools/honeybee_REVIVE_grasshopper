# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create CO2-Reduction-Measure."""


try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")

from honeybee_ph_utils.input_tools import input_to_int

try:
    from honeybee_revive.CO2_measures import CO2ReductionMeasure, CO2ReductionMeasureType
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive")


class GHCompo_CreateCO2ReductionMeasure(object):

    def __init__(
        self,
        _IGH,
        _name,
        _type,
        _year,
        _cost,
        _kg_CO2,
        _country_name,
        _labor_fraction,
    ):
        # type: (gh_io.IGH, str, str, int, float, float, str, float) -> None
        self.IGH = _IGH
        self.name = _name or "unnamed_measure"
        self.measure_type = CO2ReductionMeasureType(input_to_int(_type) or 1)
        self.year = _year or 0
        self.cost = _cost or 0.0
        self.kg_CO2 = _kg_CO2 or 0.0
        self.country_name = _country_name or "USA"
        self.labor_fraction = _labor_fraction or 0.4

    def run(self):
        # type: () -> CO2ReductionMeasure
        new_measure = CO2ReductionMeasure()
        new_measure.name = self.name
        new_measure.measure_type = self.measure_type
        new_measure.year = self.year
        new_measure.cost = self.cost
        new_measure.kg_CO2 = self.kg_CO2
        new_measure.country_name = self.country_name
        new_measure.labor_fraction = self.labor_fraction
        return new_measure
