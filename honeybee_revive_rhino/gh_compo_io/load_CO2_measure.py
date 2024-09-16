# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Load CO2-Reduction-Measure."""

import os

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")

try:
    from honeybee_revive.CO2_measures import CO2ReductionMeasure
    from honeybee_revive_standards.CO2_measures._load_CO2_measures import load_CO2_measures_from_json_file
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive")

try:
    from honeybee_revive_standards import CO2_measures
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")


class GHCompo_LoadCO2ReductionMeasure(object):

    def __init__(self, _IGH, _measure_name):
        # type: (gh_io.IGH, str) -> None
        self.IGH = _IGH
        self.measure_name = _measure_name

    def run(self):
        # type: () -> CO2ReductionMeasure | None

        # 1) -- Search through the honeybee_revive standards
        revive_measures_directory = os.path.dirname(CO2_measures.__file__)
        for f in sorted(os.listdir(revive_measures_directory)):
            if not f.endswith(".json"):
                continue

            loaded_measures = load_CO2_measures_from_json_file(os.path.join(revive_measures_directory, f))
            json_measure = loaded_measures.get(self.measure_name, None)
            if json_measure:
                return json_measure

        # 2) -- Search through the LBT standards
        # TODO: Implement this part...

        return None
