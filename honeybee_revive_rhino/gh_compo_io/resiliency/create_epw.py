# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create Resiliency EPW."""

import math
import os
from copy import copy

try:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.config import folders
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.dt import DateTime
    from ladybug.epw import EPW
    from ladybug.stat import STAT
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))


try:
    from ph_gh_component_io import gh_io, validators
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")

# ---
EXTREME_WEEK_HOURS = 168
phase_adj = [math.sin(math.pi * hr / EXTREME_WEEK_HOURS) for hr in range(EXTREME_WEEK_HOURS)]


def iterative_delta(target_return, original_week, extreme_func):
    """
    Calculate the delta value to apply to the original week to get the desired return value.
    Adapted from https://github.com/Phius-ResearchComittee/REVIVE/blob/main/REVIVE2024/weatherMorph.py

    Args:
        target_return: n-year return extreme values of dry-bulb or dewpoint
        original_week: original hourly db or dewpoint values from outage week
        extreme_func: function to apply to morphed week - max for summer and min for winter

    Returns:
        tuple: iteration count and delta value to apply to original week to get the desired return value
    """
    relaxation_factor = 0.1
    tolerance = 0.01

    delta = target_return - (sum(original_week) / len(original_week))
    morphed_week = [temp + delta * adj for temp, adj in zip(original_week, phase_adj)]
    extreme_value = extreme_func(morphed_week)

    iteration_count = 0
    while abs(target_return - extreme_value) >= tolerance:
        if iteration_count >= 100:
            print("Max iterations reached!")
            break
        iteration_count += 1
        delta += relaxation_factor * (target_return - extreme_value)
        morphed_week = [temp + delta * adj for temp, adj in zip(original_week, phase_adj)]
        extreme_value = extreme_func(morphed_week)

    return iteration_count, delta


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
        self.sat_file = _sat_file
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
                (self.sat_file is not None),
                self.winter_10yr_dry_bulb_C,
                self.winter_10yr_dew_point_C,
                self.summer_20yr_dry_bulb_C,
                self.summer_20yr_dew_point_C,
                self._run,
            ]
        )

    def check_extreme_week(self, extreme_week):
        # type: (AnalysisPeriod | None) -> AnalysisPeriod
        if not extreme_week or len(extreme_week) != 168:
            raise ValueError("The extreme week should be 168 hours long. Got: {}".format(len(extreme_week or [])))
        else:
            # -- Add a day to the start and end of the period
            # -- this is needed to ensure we have the right starting conditions (temp, RH, etc...)
            expanded_extreme_week = AnalysisPeriod.from_start_end_datetime(
                DateTime.from_hoy(extreme_week._st_time.hoy - 24),
                DateTime.from_hoy(extreme_week._end_time.hoy + 24),
                timestep=extreme_week.timestep,
            )
            print("Using Extreme Week: {}".format(expanded_extreme_week))
            return expanded_extreme_week

    def run(self):
        # type: () -> tuple[str | None, AnalysisPeriod | None, AnalysisPeriod | None]
        if not self.ready:
            return None, None, None

        # --------------------------------------------------------------------------------------------------------------
        # -- Load in the STAT and EPW files
        lb_epw = EPW(self.epw_file)
        lb_stat = STAT(self.sat_file)
        winter_period = self.check_extreme_week(lb_stat.extreme_cold_week)
        summer_period = self.check_extreme_week(lb_stat.extreme_hot_week)

        # --------------------------------------------------------------------------------------------------------------
        # -- Pull out the STAT file's Peak Winter and Peak Summer Weeks from the Ladybug EPW file
        dry_bulb_deg_C = lb_epw.dry_bulb_temperature  # type: HourlyContinuousCollection
        dew_point_deg_C = lb_epw.dew_point_temperature  # type: HourlyContinuousCollection

        winter_dry_bulb_deg_C = dry_bulb_deg_C.filter_by_analysis_period(lb_stat.extreme_cold_week).values
        winter_dew_point_deg_C = dew_point_deg_C.filter_by_analysis_period(lb_stat.extreme_cold_week).values

        summer_dry_bulb_deg_C = dry_bulb_deg_C.filter_by_analysis_period(lb_stat.extreme_hot_week).values
        summer_dew_point_deg_C = dew_point_deg_C.filter_by_analysis_period(lb_stat.extreme_hot_week).values

        # --------------------------------------------------------------------------------------------------------------
        # -- Calculate the Phius-REVIVE Weather-Morphing Factors
        # -- Adapted from https://github.com/Phius-ResearchComittee/REVIVE/blob/main/REVIVE2024/weatherMorph.py
        iters, winter_dry_bulb_factor = iterative_delta(self.winter_10yr_dry_bulb_C, winter_dry_bulb_deg_C, min)
        print("Winter Dry-Bulb Factor: {:,.3f} (took {} iterations)".format(winter_dry_bulb_factor, iters))

        iters, winter_dew_point_factor = iterative_delta(self.winter_10yr_dew_point_C, winter_dew_point_deg_C, min)
        print("Winter Dew-Point Factor: {:,.3f} (took {} iterations)".format(winter_dew_point_factor, iters))

        iters, summer_dry_bulb_factor = iterative_delta(self.summer_20yr_dry_bulb_C, summer_dry_bulb_deg_C, max)
        print("Summer Dry-Bulb Factor: {:,.3f} (took {} iterations)".format(summer_dry_bulb_factor, iters))

        iters, summer_dew_point_factor = iterative_delta(self.summer_20yr_dew_point_C, summer_dew_point_deg_C, max)
        print("Summer Dew-Point Factor: {:,.3f} (took {} iterations)".format(summer_dew_point_factor, iters))

        # --------------------------------------------------------------------------------------------------------------
        # -- Apply the factors to the EPW File and generate a new EPW file
        new_epw = copy(lb_epw)

        # TODO.....

        # --------------------------------------------------------------------------------------------------------------
        # -- Save the new EPW file to disk
        _file_name_ = "Phius_REVIVE_2024_{}".format(os.path.basename(str(new_epw.file_path)))
        epw_file_ = os.path.join(self.folder, _file_name_)
        new_epw.save(epw_file_)

        return epw_file_, winter_period, summer_period
