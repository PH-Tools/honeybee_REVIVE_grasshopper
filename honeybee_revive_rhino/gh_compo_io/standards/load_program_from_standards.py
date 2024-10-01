# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Load REVIVE Program from Standards."""

import os

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    import honeybee_revive_standards
    from honeybee_revive_standards.programtypes._load_programs import load_programs_from_json_file
    from honeybee_revive_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


def names_match(_name_1, _name_2):
    # type: (str, str) -> bool
    """Check if two names match (lower-cased)."""
    return str(_name_1).lower().replace(" ", "_") == str(_name_2).lower().replace(" ", "_")


class GHCompo_LoadProgramFromStandards(object):

    def __init__(self, _IGH, _standards_dir, _program_name, *args, **kwargs):
        # type: (gh_io.IGH, str | None, str | None, list, dict) -> None
        self.IGH = _IGH
        self.standards_dir = _standards_dir or os.path.dirname(honeybee_revive_standards.__file__)
        self.program_name = _program_name or "rv2024_Residence"

    def create_schedules_dict(self):
        # type: () -> dict[str, ScheduleRuleset]
        schedules_dir = os.path.join(self.standards_dir, "schedules")
        if not os.path.exists(schedules_dir):
            msg = "No 'schedules' directory found inside: '{}'.".format(self.standards_dir)
            raise ValueError(msg)

        schedules_dict = {}
        for schedule_filename in os.listdir(schedules_dir):
            if not schedule_filename.endswith(".json"):
                continue
            schedules_dict.update(load_schedules_from_json_file(os.path.join(schedules_dir, schedule_filename)))

        return schedules_dict

    def load_program_from_standards_dir(self, _schedules_dict):
        # type: (dict[str, ScheduleRuleset]) -> ProgramType | None
        programs_dir = os.path.join(self.standards_dir, "programtypes")
        if not os.path.exists(programs_dir):
            msg = "No 'programtypes' directory found inside: '{}'.".format(self.standards_dir)
            raise ValueError(msg)

        for program_filename in os.listdir(programs_dir):
            if not program_filename.endswith(".json"):
                continue

            for program_name, program in load_programs_from_json_file(
                os.path.join(programs_dir, program_filename), _schedules_dict=_schedules_dict
            ).items():
                if names_match(program_name, self.program_name):
                    return program

    def run(self):
        # type: () -> ProgramType | None
        if not os.path.exists(self.standards_dir):
            msg = "No directory found at: '{}'.".format(self.standards_dir)
            raise ValueError(msg)

        program_found = self.load_program_from_standards_dir(self.create_schedules_dict())
        if program_found:
            return program_found

        # TODO: Search through the LBT standards directories

        # -- Raise warning if no program was found
        self.IGH.warning("The Program '{}' was not found in the standards directory.".format(self.program_name))
        return None
