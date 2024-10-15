# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""UTILITY: Loaders for Revive Programs and Schedules."""

import os

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    from honeybee_revive_standards.programtypes._load_programs import load_programs_from_json_file
    from honeybee_revive_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")


def names_match(_name_1, _name_2):
    # type: (str, str) -> bool
    """Check if two names match (lower-cased)."""

    return str(_name_1).lower().replace(" ", "_") == str(_name_2).lower().replace(" ", "_")


def load_schedules_from_standards(_standards_dir):
    # type: (str) -> dict[str, ScheduleRuleset]
    """Create a dictionary of all schedules in the standards directory."""

    schedules_dir = os.path.join(_standards_dir, "schedules")
    if not os.path.exists(schedules_dir):
        msg = "No 'schedules' directory found inside: '{}'.".format(_standards_dir)
        raise ValueError(msg)

    schedules_dict = {}
    for schedule_filename in os.listdir(schedules_dir):
        if not schedule_filename.endswith(".json"):
            continue
        schedules_dict.update(load_schedules_from_json_file(os.path.join(schedules_dir, schedule_filename)))

    return schedules_dict


def load_program_from_standards_dir(_standards_dir, _program_name, _schedules_dict):
    # type: (str, str, dict[str, ScheduleRuleset]) -> ProgramType | None
    """Load a Revive Program from the standards directory."""

    programs_dir = os.path.join(_standards_dir, "programtypes")
    if not os.path.exists(programs_dir):
        msg = "No 'programtypes' directory found inside: '{}'.".format(_standards_dir)
        raise ValueError(msg)

    for program_filename in os.listdir(programs_dir):
        if not program_filename.endswith(".json"):
            continue

        for program_name, program in load_programs_from_json_file(
            os.path.join(programs_dir, program_filename), _schedules_dict=_schedules_dict
        ).items():
            if names_match(program_name, _program_name):
                return program


def load_program_and_schedules(_standards_dir, _program_name):
    # type: (str, str) -> ProgramType | None
    """Load a Revive Program and Schedules from the default standards directory."""

    return load_program_from_standards_dir(_standards_dir, _program_name, load_schedules_from_standards(_standards_dir))
