# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Add REVIVE HVAC Equipment Properties to Rooms."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_revive.hvac.equipment import PhiusReviveHVACEquipment
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_revive:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_AddHvacEquipmentPropertiesToRooms(object):

    def __init__(self, _IGH, _revive_equipment, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, list[PhiusReviveHVACEquipment], list[Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.revive_equipment = _revive_equipment
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> list[Room]
        """Add HVAC Equipment Properties to Rooms.

        Have to do it this way so that we avoid duplicated Equipment 'upstream'
        on the Room's properties.
        """

        # -- Collect all of the unique ReviveProperties first...
        unique_revive_props = {}  # type: dict[str, Any]
        for room in self.hb_rooms:
            rm_prop_e = getattr(room.properties, "energy")
            if not rm_prop_e.hvac:
                continue
            unique_revive_props[room.identifier] = rm_prop_e.hvac.properties.revive

        # -- Add each of the HVAC-Equipment items to each of the ReviveProperties
        unique_revive_props_with_equip = {}
        for identifier, original_revive_prop in unique_revive_props.items():
            new_prop = original_revive_prop.duplicate()
            unique_revive_props_with_equip[identifier] = new_prop
            for rv_equip in self.revive_equipment:
                new_prop.equipment_collection.add_equipment(rv_equip)

        # -- Apply the new Revive Properties with the Equipment back onto the HB-Rooms
        new_rooms_ = []
        for room in self.hb_rooms:
            new_room = room.duplicate()
            rm_prop_e = getattr(new_room.properties, "energy")
            if not rm_prop_e.hvac:
                self.IGH.warning("Room '{}' does not have an HVAC system.".format(room.display_name))
                continue
            revive_prop = unique_revive_props_with_equip[room.identifier]
            rm_prop_e.hvac.properties._revive = revive_prop
            new_rooms_.append(new_room)

        return new_rooms_
