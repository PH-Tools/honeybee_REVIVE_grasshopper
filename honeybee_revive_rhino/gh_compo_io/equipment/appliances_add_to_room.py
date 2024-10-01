# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Add REVIVE Appliances to Rooms."""


try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
    from honeybee_energy.load.process import Process
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


class GHCompo_AddReviveAppliancesToRooms(object):

    def __init__(self, _IGH, _appliances, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, list[Process], list[Room], list, dict) -> None
        self.IGH = _IGH
        self.appliances = [ap for ap in _appliances if ap is not None]
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> list[Room]

        rooms_ = []
        for room in self.hb_rooms:
            new_room = room.duplicate()
            room_prop = getattr(new_room.properties, "energy")  # type: RoomEnergyProperties

            for appliance in self.appliances:
                new_app = appliance.duplicate()
                new_app.unlock()
                new_app.display_name = "{}-{}".format(appliance.display_name, room.display_name)
                new_app.lock()
                room_prop.add_process_load(new_app)

            rooms_.append(new_room)

        return rooms_
