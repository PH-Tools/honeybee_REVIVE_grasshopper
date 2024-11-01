# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Load REVIVE Schedules from Standards."""

import os

try:
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    import honeybee_revive_standards
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")

try:
    import honeybee_revive_standards

    from honeybee_revive_rhino.gh_compo_io.standards._load import load_schedules_from_standards
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


class GHCompo_LoadSchedulesFromStandards(object):

    def __init__(self, _IGH, _standards_dir, *args, **kwargs):
        # type: (gh_io.IGH, str | None, list, dict) -> None
        self.IGH = _IGH
        self.standards_dir = _standards_dir or os.path.dirname(honeybee_revive_standards.__file__)

    def run(self):
        # type: () -> list[ScheduleRuleset]

        if not os.path.exists(self.standards_dir):
            msg = "No directory found at: '{}'.".format(self.standards_dir)
            raise ValueError(msg)

        schedules_dict = load_schedules_from_standards(self.standards_dir)

        return [schedules_dict[s] for s in sorted(schedules_dict.keys())]
