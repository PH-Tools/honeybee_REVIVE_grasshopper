# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create Resiliency EPW."""

import os

try:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.config import folders
    from ladybug.epw import EPW
    from ladybug.stat import STAT
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")

try:
    from ladybug_revive.resiliency_epw import generate_ladybug_epw
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_revive:\n\t{}".format(e))


# ----------------------------------------------------------------------------------------------------------------------
# -- GH Interface


class GHCompo_CreateResiliencyEPWFile(object):
    winter_10yr_dry_bulb_C = validators.UnitDegreeC("winter_10yr_dry_bulb_C")
    winter_10yr_dew_point_C = validators.UnitDegreeC("winter_10yr_dew_point_C")
    summer_20yr_dry_bulb_C = validators.UnitDegreeC("summer_20yr_dry_bulb_C")
    summer_20yr_dew_point_C = validators.UnitDegreeC("summer_20yr_dew_point_C")

    def __init__(
        self,
        _IGH,
        _epw_file,
        _sat_file,
        _folder,
        winter_10yr_dry_bulb_C,
        winter_10yr_dew_point_C,
        summer_20yr_dry_bulb_C,
        summer_20yr_dew_point_C,
        _run,
        *arg,
        **kwargs
    ):
        # type: (gh_io.IGH, str, str, str, float, float, float, float, bool, list, dict) -> None
        self.IGH = _IGH
        self.epw_file = _epw_file
        self.stat_file = _sat_file
        self.folder = folders.default_epw_folder if _folder is None else _folder
        self.winter_10yr_dry_bulb_C = winter_10yr_dry_bulb_C
        self.winter_10yr_dew_point_C = winter_10yr_dew_point_C
        self.summer_20yr_dry_bulb_C = summer_20yr_dry_bulb_C
        self.summer_20yr_dew_point_C = summer_20yr_dew_point_C

        self._run = _run

    @property
    def ready(self):
        # type: () -> bool
        return all(
            [
                (self.epw_file is not None),
                (self.stat_file is not None),
                self.winter_10yr_dry_bulb_C,
                self.winter_10yr_dew_point_C,
                self.summer_20yr_dry_bulb_C,
                self.summer_20yr_dew_point_C,
                self._run,
            ]
        )

    def run(self):
        # type: () -> tuple[str | None, AnalysisPeriod | None, AnalysisPeriod | None]
        if not self.ready:
            return None, None, None

        # --------------------------------------------------------------------------------------------------------------
        # -- Generate a new Ladybug EPW with the adjustment factors applied
        print("Loading the EPW file: {}".format(self.epw_file))
        print("Loading the STAT file: {}".format(self.stat_file))
        new_ladybug_epw, winter_outage_period_expanded, summer_outage_period_expanded = generate_ladybug_epw(
            EPW(self.epw_file),
            STAT(self.stat_file),
            self.winter_10yr_dry_bulb_C,
            self.winter_10yr_dew_point_C,
            self.summer_20yr_dry_bulb_C,
            self.summer_20yr_dew_point_C,
        )

        # --------------------------------------------------------------------------------------------------------------
        # -- Save the new Ladybug EPW data to file
        _file_name_ = "Phius_REVIVE_2024_{}".format(os.path.basename(str(new_ladybug_epw.file_path)))
        epw_filepath_ = os.path.join(self.folder, _file_name_)
        new_ladybug_epw.save(epw_filepath_)

        return epw_filepath_, winter_outage_period_expanded, summer_outage_period_expanded
