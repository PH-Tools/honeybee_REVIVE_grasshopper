# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set PV-Shade REVIVE Properties."""

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.shade import Shade
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.shade import ShadeEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_revive.properties.generator.pv import PvPropertiesReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))


class GHCompo_SetPvShadeProperties(object):

    def __init__(self, _IGH, _cost, _labor_fraction, _lifetime_years, _hb_shades, *args, **kwargs):
        # type: (gh_io.IGH, float, float, int, list[Shade], *Any, **Any) -> None
        self.IGH = _IGH
        self.cost = _cost
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years
        self.hb_shades = _hb_shades

    def run(self):
        # type: () -> list[Shade]

        new_shades_ = []  # type: list[Shade]
        for shade in self.hb_shades:
            new_shade = shade.duplicate()

            shade_prop_e = getattr(shade.properties, "energy")  # type: ShadeEnergyProperties
            shad_pv_prop = shade_prop_e.pv_properties

            if not shad_pv_prop:
                raise ValueError("Shade: {} does not have PV applied..".format(new_shade.display_name))

            shade_pv_prop = getattr(shad_pv_prop.properties, "revive")  # type: PvPropertiesReviveProperties
            shade_pv_prop.cost = self.cost
            shade_pv_prop.labor_fraction = self.labor_fraction
            shade_pv_prop.lifetime_years = self.lifetime_years

            new_shades_.append(new_shade)

        return new_shades_
