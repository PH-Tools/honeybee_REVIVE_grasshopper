# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Material or Construction REVIVE Properties."""

try:
    from ph_units.unit_type import Unit
except ImportError:
    raise ImportError("\nFailed to import ph_units")

try:
    from ph_gh_component_io import gh_io, validators
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


# ----------------------------------------------------------------------------------------------------------------------
# -- Protocol Classes


class __SupportsReviveAttributesProtocol__(object):
    """Protocol class for type-checking."""

    def __init__(self):
        self.kg_CO2_per_m2 = Unit(0, "KG/M2")
        self.cost_per_m2 = Unit(0, "COST/M2")
        self.labor_fraction = 0.0
        self.lifetime_years = 0

    def __new__(cls):
        raise NotImplementedError("This is a protocol class and should not be instantiated.")


class __SupportsRevivePropertiesProtocol__(object):
    """Protocol class for type-checking."""

    def __init__(self):
        self.revive = __SupportsReviveAttributesProtocol__()

    def __new__(cls):
        raise NotImplementedError("This is a protocol class and should not be instantiated.")


class __SupportsPropertiesProtocol__(object):
    """Protocol class for type-checking."""

    def __init__(self):
        self.properties = __SupportsRevivePropertiesProtocol__()

    def duplicate(self):
        # type: () -> __SupportsPropertiesProtocol__
        raise NotImplementedError("This is a protocol class and should not be instantiated.")


# ----------------------------------------------------------------------------------------------------------------------


class GHCompo_SetMaterialProperties(object):
    kg_CO2_per_m2 = validators.UnitKG_M2("kg_CO2_per_m2", default=0.0)
    cost_per_m2 = validators.UnitCost_M2("cost_per_m2", default=0.0)
    labor_fraction = validators.FloatPercentage("labor_fraction", default=0.0)

    def __init__(
        self, _IGH, _hb_object, _kg_CO2_per_m2, _cost_per_m2, _labor_fraction, _lifetime_years, *args, **kwargs
    ):
        # type: (gh_io.IGH, __SupportsPropertiesProtocol__, float, float, float, int, list, dict) -> None
        self.IGH = _IGH
        self.hb_object = _hb_object
        self.kg_CO2_per_m2 = _kg_CO2_per_m2
        self.cost_per_m2 = _cost_per_m2
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years

    def run(self):
        # type: () -> __SupportsPropertiesProtocol__ | None
        if not self.hb_object:
            return None
        new_hb_obj = self.hb_object.duplicate()
        new_mat_prop = new_hb_obj.properties.revive
        new_mat_prop.kg_CO2_per_m2 = Unit(self.kg_CO2_per_m2, "KG/M2")
        new_mat_prop.cost_per_m2 = Unit(self.cost_per_m2, "COST/M2")
        new_mat_prop.labor_fraction = self.labor_fraction
        new_mat_prop.lifetime_years = self.lifetime_years
        return new_hb_obj
