# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Load REVIVE Program from Standards."""

import os

try:
    from honeybee_energy.programtype import ProgramType
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    import honeybee_revive_standards
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")

try:
    import honeybee_revive_standards

    from honeybee_revive_rhino.gh_compo_io.standards._load import load_program_and_schedules
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive_rhino: {0}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


def names_match(_name_1, _name_2):
    # type: (str, str) -> bool
    """Check if two names match (lower-cased)."""
    return str(_name_1).lower().replace(" ", "_") == str(_name_2).lower().replace(" ", "_")


class GHCompo_LoadProgramFromStandards(object):

    DEFAULT_PROGRAM_NAME = "rv2024_Residence_Annual"

    def __init__(self, _IGH, _standards_dir, _program_name, *args, **kwargs):
        # type: (gh_io.IGH, str | None, str | None, list, dict) -> None
        self.IGH = _IGH
        self.standards_dir = _standards_dir or os.path.dirname(honeybee_revive_standards.__file__)
        self.program_name = _program_name or self.DEFAULT_PROGRAM_NAME

    def run(self):
        # type: () -> ProgramType | None
        if not os.path.exists(self.standards_dir):
            msg = "No directory found at: '{}'.".format(self.standards_dir)
            raise ValueError(msg)

        program_found = load_program_and_schedules(self.standards_dir, self.program_name)
        if program_found:
            return program_found

        # TODO: Search through the LBT standards directories

        # -- Raise warning if no program was found
        self.IGH.warning("The Program '{}' was not found in the standards directory.".format(self.program_name))
        return None
