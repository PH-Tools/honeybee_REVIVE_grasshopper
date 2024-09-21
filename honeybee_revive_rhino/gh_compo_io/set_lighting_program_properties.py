# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set REVIVE Lighting Program Properties."""

try:
    from honeybee_energy.load.lighting import Lighting
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_revive.properties.load.lighting import LightingReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_revive:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SetLightingProgramProperties(object):
    def __init__(self, _IGH, _cost, _labor_fraction, _lifetime_years, _hbe_lighting, *args, **kwargs):
        # type: (gh_io.IGH, float, float, int, Lighting, list, dict) -> None
        self.IGH = _IGH
        self.cost = _cost
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years
        self.hbe_lighting = _hbe_lighting

    def run(self):
        # type:() -> Lighting | None

        if self.hbe_lighting is None:
            return None

        new_lighting = self.hbe_lighting.duplicate()  # type: Lighting # type: ignore

        lighting_prop = getattr(new_lighting.properties, "revive")  # type: LightingReviveProperties
        lighting_prop.cost = self.cost
        lighting_prop.labor_fraction = self.labor_fraction
        lighting_prop.lifetime_years = self.lifetime_years

        return new_lighting
