# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Appliance REVIVE Properties."""

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

# ----------------------------------------------------------------------------------------------------------------------
# -- Protocol Classes


class __SupportsReviveAttributesProtocol__(object):
    """Protocol class for type-checking."""

    def __init__(self):
        self.cost = 0.0
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


class GHCompo_SetApplianceReviveProperties(object):
    kg_CO2_per_m2 = ghio_validators.UnitKG_M2("kg_CO2_per_m2", default=0.0)
    cost_per_m2 = ghio_validators.UnitCost_M2("kg_CO2_per_m2", default=0.0)
    labor_fraction = ghio_validators.FloatPercentage("labor_fraction", default=0.0)

    def __init__(self, _IGH, _cost, _labor_fraction, _lifetime_years, _hb_appliance, *args, **kwargs):
        # type: (gh_io.IGH, float, float, int, __SupportsPropertiesProtocol__, list, dict) -> None
        self.IGH = _IGH
        self.cost = _cost
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years
        self.hb_appliance = _hb_appliance

    def run(self):
        # type: () -> __SupportsPropertiesProtocol__ | None
        if not self.hb_appliance:
            return None
        new_hb_obj = self.hb_appliance.duplicate()
        new_mat_prop = new_hb_obj.properties.revive
        new_mat_prop.cost = self.cost
        new_mat_prop.labor_fraction = self.labor_fraction
        new_mat_prop.lifetime_years = self.lifetime_years
        return new_hb_obj
