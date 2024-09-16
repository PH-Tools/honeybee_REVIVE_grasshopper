# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Material REVIVE Properties."""

try:
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SetMaterialProperties(object):
    kg_CO2_per_m2 = ghio_validators.UnitKG_M2("kg_CO2_per_m2", default=0.0)
    cost_per_m2 = ghio_validators.UnitCost_M2("kg_CO2_per_m2", default=0.0)
    labor_fraction = ghio_validators.FloatPercentage("labor_fraction", default=0.0)

    def __init__(
        self, _IGH, _material, _kg_CO2_per_m2, _cost_per_m2, _labor_fraction, _lifetime_years, *args, **kwargs
    ):
        # type: (gh_io.IGH, EnergyMaterial, str, str, float, int, list, dict) -> None
        self.IGH = _IGH
        self.material = _material
        self.kg_CO2_per_m2 = _kg_CO2_per_m2
        self.cost_per_m2 = _cost_per_m2
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years

    def run(self):
        # type: () -> EnergyMaterial | None
        if not self.material:
            return None
        new_material = self.material.duplicate()
        return new_material
