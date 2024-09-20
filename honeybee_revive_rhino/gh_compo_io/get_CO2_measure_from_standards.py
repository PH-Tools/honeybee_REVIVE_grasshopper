# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Get REVIVE CO2-Measures from Standards Library."""

import os

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")

try:
    from honeybee_revive.CO2_measures import CO2ReductionMeasure
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive")

try:
    from honeybee_revive_standards import CO2_measures
    from honeybee_revive_standards.CO2_measures._load_CO2_measures import load_CO2_measures_from_json_file
except ImportError:
    raise ImportError("\nFailed to import honeybee_revive_standards")


class GHCompo_LoadCO2ReductionMeasure(object):

    def __init__(self, _IGH, _measure_names, *args, **kwargs):
        # type: (gh_io.IGH, list[str], list, dict) -> None
        self.IGH = _IGH
        self.measure_names = _measure_names

    def run(self):
        # type: () -> list[CO2ReductionMeasure]
        measures_ = []  # type: list[CO2ReductionMeasure]
        # 1) -- Search through the honeybee_revive standards
        revive_measures_directory = os.path.dirname(CO2_measures.__file__)
        for f in sorted(os.listdir(revive_measures_directory)):
            if not f.endswith(".json"):
                continue

            loaded_measures = load_CO2_measures_from_json_file(os.path.join(revive_measures_directory, f))

            for appliance_name in self.measure_names:
                measure = loaded_measures.get(appliance_name, None)

                if measure:
                    measures_.append(measure)

        # 2) -- Search through the LBT standards
        # TODO: Implement this part...

        # 3) Check if any measure names are not found
        found_measure_names = {a.name for a in measures_}
        not_found_measure_names = set(self.measure_names) - found_measure_names
        if not_found_measure_names:
            self.IGH.warning(
                "The following CO2-Measure names were not found in the standards library:\n"
                "{}".format(", ".join(not_found_measure_names))
            )

        return measures_
