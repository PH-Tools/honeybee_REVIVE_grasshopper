# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create REVIVE HVAC Equipment Properties."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy_revive.hvac.equipment import PhiusReviveHVACEquipment
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_revive:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateReviveHvacEquipmentProperties(object):

    def __init__(self, _IGH, _display_name, _cost, _labor_fraction, _lifetime_years, *args, **kwargs):
        # type: (gh_io.IGH, str, float, float, int, *Any, **Any) -> None
        self.IGH = _IGH
        self.display_name = _display_name
        self.cost = _cost or 0.0
        self.labor_fraction = _labor_fraction or 0.0
        self.lifetime_years = _lifetime_years or 0

    def run(self):
        # type: () -> PhiusReviveHVACEquipment | None
        if not self.display_name:
            return None

        new_equipment = PhiusReviveHVACEquipment(
            display_name=self.display_name,
            cost=self.cost,
            labor_fraction=self.labor_fraction,
            lifetime_years=self.lifetime_years,
        )
        new_equipment.lock()  # type: ignore
        return new_equipment
