# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Room REVIVE Lighting Properties."""

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
    from honeybee_energy.load.lighting import Lighting
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_revive.properties.load.lighting import LightingReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_revive:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_SetRoomLightingProperties(object):
    def __init__(self, _IGH, _cost, _labor_fraction, _lifetime_years, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, float, float, int, list[Room], list, dict) -> None
        self.IGH = _IGH
        self.cost = _cost
        self.labor_fraction = _labor_fraction
        self.lifetime_years = _lifetime_years
        self.hb_rooms = _hb_rooms

    def run(self):
        # type:() -> list[Room]

        # --------------------------------------------------------------------------------------------------------------
        # -- Collect all of the unique Lighting programs from all of the rooms.
        unique_lighting_programs = {}  # type: dict[str, Lighting]
        for room in self.hb_rooms:
            room_hbe_prop = getattr(room.properties, "energy")  # type: RoomEnergyProperties
            lighting_program = room_hbe_prop.lighting

            # ----------------------------------------------------------------------------------------------------------
            if lighting_program is None:
                msg = "Room '{}' does not have a lighting program.".format(room.display_name)
                self.IGH.error(msg)

            # ----------------------------------------------------------------------------------------------------------
            # -- Set the properties for each of the lighting programs
            new_lighting = lighting_program.duplicate()
            lighting_prop = getattr(new_lighting.properties, "revive")  # type: LightingReviveProperties
            lighting_prop.cost = self.cost
            lighting_prop.labor_fraction = self.labor_fraction
            lighting_prop.lifetime_years = self.lifetime_years

            # ----------------------------------------------------------------------------------------------------------
            unique_lighting_programs[lighting_program.identifier] = new_lighting  # type: ignore

        # --------------------------------------------------------------------------------------------------------------
        # -- Duplicate the room, then re-set the lighting program

        new_rooms_ = []  # type: list[Room]
        for room in self.hb_rooms:
            new_room = room.duplicate()
            new_room_prop_e = getattr(new_room.properties, "energy")  # type: RoomEnergyProperties
            new_room_prop_e.lighting = unique_lighting_programs[new_room_prop_e.lighting.identifier]
            new_rooms_.append(new_room)

        return new_rooms_
