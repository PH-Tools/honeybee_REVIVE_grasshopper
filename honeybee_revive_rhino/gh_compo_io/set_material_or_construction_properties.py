# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Material or Construction REVIVE Properties."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.unit_type import Unit
except ImportError:
    raise ImportError("\nFailed to import ph_units")


class __SupportsReviveAttributesProtocol__(object):
    """Protocol class for type-checking."""

    def __init__(self):
        self.kg_CO2_per_m2 = Unit(0, "KG/M2")
        self.cost_per_m2 = Unit(0, "COST/M2")
        self.labor_fraction = 0.0
        self.lifetime_years = 0

    def __new__(cls):
        raise NotImplementedError("This is a protocol class and should not be instantiated.")


class GHCompo_SetMaterialOrConstructionProperties(object):
    kg_CO2_per_m2 = ghio_validators.UnitKG_M2("kg_CO2_per_m2", default=0.0)
    cost_per_m2 = ghio_validators.UnitCost_M2("kg_CO2_per_m2", default=0.0)
    labor_fraction = ghio_validators.FloatPercentage("labor_fraction", default=0.0)

    def __init__(
        self, _IGH, _hb_object, _kg_CO2_per_m2, _cost_per_m2, _labor_fraction, _lifetime_years, *args, **kwargs
    ):
        # type: (gh_io.IGH, EnergyMaterial, float, float, float, int, list, dict) -> None
        self.IGH = _IGH
        self.hb_object = _hb_object
        self.kg_CO2_per_m2 = _kg_CO2_per_m2
        self.cost_per_m2 = _cost_per_m2
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years

    def run(self):
        # type: () -> Any
        if not self.hb_object:
            return None
        new_hb_obj = self.hb_object.duplicate()
        new_mat_prop = getattr(new_hb_obj.properties, "revive")  # type: __SupportsReviveAttributesProtocol__
        new_mat_prop.kg_CO2_per_m2 = Unit(self.kg_CO2_per_m2, "KG/M2")
        new_mat_prop.cost_per_m2 = Unit(self.cost_per_m2, "COST/M2")
        new_mat_prop.labor_fraction = self.labor_fraction
        new_mat_prop.lifetime_years = self.lifetime_years
        return new_hb_obj
