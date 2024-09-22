# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Load REVIVE Appliance from Standards Library."""

import os

try:
    from honeybee_energy.load.process import Process
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")

try:
    from honeybee_revive_standards import schedules
    from honeybee_revive_standards import appliances
    from honeybee_revive_standards.appliances._load_appliances import load_abridged_appliances_from_json_file
    from honeybee_revive_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")


class GHCompo_LoadReviveApplianceFromStandardsLibrary(object):

    def __init__(self, _IGH, _appliance_names, *args, **kwargs):
        # type: (gh_io.IGH, list[str], list, dict) -> None
        self.IGH = _IGH
        self.appliance_names = _appliance_names

    def run(self):
        # type: () -> list[Process]

        # 1)-- Build all the Schedules from the standards
        schedules_dict = {}
        revive_schedules_directory = os.path.dirname(schedules.__file__)
        for schedule_filename in sorted(os.listdir(revive_schedules_directory)):
            if not schedule_filename.endswith(".json"):
                continue
            schedules_dict.update(
                load_schedules_from_json_file(os.path.join(revive_schedules_directory, schedule_filename))
            )

        # 2) -- Search through the Appliances (Process) from the standards
        appliances_ = []  # type: list[Process]
        revive_appliances_directory = os.path.dirname(appliances.__file__)
        for appliance_filename in sorted(os.listdir(revive_appliances_directory)):
            if not appliance_filename.endswith(".json"):
                continue

            loaded_appliances = load_abridged_appliances_from_json_file(
                os.path.join(revive_appliances_directory, appliance_filename),
                _schedules_dict=schedules_dict,
            )

            for appliance_name in self.appliance_names:
                json_appliance = loaded_appliances.get(appliance_name, None)

                if json_appliance:
                    appliances_.append(json_appliance)

        # 2) -- Search through the LBT standards
        # TODO: Implement this part...

        # 3) Check if any appliance names are not found
        found_appliance_names = {a.display_name for a in appliances_}
        not_found_appliance_names = set(self.appliance_names) - found_appliance_names
        if not_found_appliance_names:
            self.IGH.warning(
                "The following appliance names were not found in the standards library:\n"
                "{}".format(", ".join(not_found_appliance_names))
            )

        return appliances_
