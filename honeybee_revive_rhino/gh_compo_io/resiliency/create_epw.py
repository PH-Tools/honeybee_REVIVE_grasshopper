# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create Resiliency EPW."""

import math
import os
from copy import copy

try:
    from itertools import izip as zip  # Using Python2.x # type: ignore
except ImportError:
    pass  # Using Python 3.x

try:
    from typing import Callable
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.config import folders
    from ladybug.datacollection import HourlyContinuousCollection, HourlyDiscontinuousCollection
    from ladybug.dt import DateTime
    from ladybug.epw import EPW
    from ladybug.stat import STAT
    from ladybug.header import Header
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


# ----------------------------------------------------------------------------------------------------------------------
# -- Functions for calculating the Phius2024 REVIVE adjustment factors


def calculate_adjustment_factor(_target_return, _original_week, _extreme_func, _relaxation_factor=0.1, _tolerance=0.01):
    # type: (float, list[float], Callable, float, float) -> tuple[int, float]
    """
    Calculate the delta value for drybulb and dewpoint temps to apply to the original EPW values.
    Adapted from https://github.com/Phius-ResearchComittee/REVIVE/blob/main/REVIVE2024/weatherMorph.py

    See also Section 6.1.2.1 'Resilience Extreme Week Morphing Algorithm' Phius Revive 2024 Retrofit Standard for Buildings v24.1.1:
        > Iteration to determine Delta_dry and Delta_dew:
        > Delta_init = T_return - avg(T_x_week)
        > T_return are the n-year return extreme values of DB and dewpoint, converted from DB and Wet bulb, from ASHRAE Climatic Design Conditions data.
        > For winter, use the 10-year return values.
        > For summer, use the 20-year return values.
        > Delta = Delta_init
        > Repeat
        > K is a relaxation factor = 0.1
        > X = [ max(T_x_week2) for hot week, min(T_x_week2) for cold week ]
        > Delta_next = Delta + K * (T_return_X)
        > Delta = Delta_next
        > Until abs(T_return_X) < tolerance ~ 0.01 F

    Args:
        target_return: n-year return extreme values of dry-bulb or dewpoint
        original_week: original hourly db or dewpoint values from outage week
        extreme_func: function to apply to morphed week: max() for summer and min() for winter

    Returns:
        tuple: iteration count and delta value to apply to original week to get the desired return value
    """
    phase_adjustment = [math.sin(math.pi * hr / len(_original_week)) for hr in range(len(_original_week))]

    # -- Starting conditions
    delta = _target_return - (sum(_original_week) / len(_original_week))
    morphed_week = [temp + delta * adj for temp, adj in zip(_original_week, phase_adjustment)]
    extreme_value = _extreme_func(morphed_week)

    # -- Iteration to determine adjustment factor
    iteration_count = 0
    while abs(_target_return - extreme_value) >= _tolerance:
        if iteration_count >= 100:
            print("Max iterations reached!")
            break
        iteration_count += 1
        delta += _relaxation_factor * (_target_return - extreme_value)
        morphed_week = [temp + delta * adj for temp, adj in zip(_original_week, phase_adjustment)]
        extreme_value = _extreme_func(morphed_week)

    return iteration_count, delta


def apply_factor_to_hourly_value(_temp, _hour, _factor, _period_total_hours):
    # type: (float, int, float, int) -> float
    """
    Apply the Phius2024 REVIVE adjustment factor to a single hourly value based.

    See also Section 6.1.2.1 'Resilience Extreme Week Morphing Algorithm' Phius Revive 2024 Retrofit Standard for Buildings v24.1.1:
        > T_x_week2_dry_h = T_x_week_dry_h + Delta_dry*sin(phase)
        > T_x_week2_dew_h = T_x_week_dew_h + Delta_dew*sin(phase)
        > T_x_week is the temperature history in the extreme week period of the EPW STAT file.
        > T_x_week2 is the morphed temperature history.
        > h is the hour within the outage period, 0 ≤ h ≤ h_out
        > h_out is the outage duration in hours minus 1
        > h_out = 167
        > Phase_h = math.pi * h / h_out
    """

    return _temp + _factor * math.sin(math.pi * _hour / _period_total_hours)


def apply_adjustment_factor_to_epw_data(_epw_data, _period_values, _period, _factor):
    # type: (HourlyContinuousCollection, list[float], AnalysisPeriod, float) -> HourlyContinuousCollection
    """Apply the Phius2024 REVIVE adjustment factor to all of the EPW data for a specific period."""

    start_index = min(_period.hoys_int)
    end_index = max(_period.hoys_int) + 1

    adjusted_temps = [
        apply_factor_to_hourly_value(temp, hour, _factor, len(_period_values))
        for hour, temp in enumerate(_period_values)
    ]

    new_values = list(_epw_data.values)
    new_values[start_index:end_index] = adjusted_temps

    return HourlyContinuousCollection(header=_epw_data.header, values=new_values)


def check_dew_point_temperature(_dew_point, _dry_bulb):
    # type: (HourlyContinuousCollection, HourlyContinuousCollection) -> HourlyContinuousCollection
    """Check the dew-point temperature to make sure it is never higher than the dry-bulb temperature."""

    new_values = [min(dew, dry) for dew, dry in zip(_dew_point.values, _dry_bulb.values)]

    return HourlyContinuousCollection(header=_dew_point.header, values=new_values)


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
        # type: (AnalysisPeriod | None) -> tuple[AnalysisPeriod, AnalysisPeriod]
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
            return extreme_week, expanded_extreme_week

    def filter_by_analysis_period(self, data, analysis_period):
        # type: (HourlyContinuousCollection | HourlyDiscontinuousCollection, AnalysisPeriod) -> list[float]
        """Wrap the LBT .filter_by_analysis_period() method so we can type it properly."""

        return data.filter_by_analysis_period(analysis_period).values  # type: ignore

    def run(self):
        # type: () -> tuple[str | None, AnalysisPeriod | None, AnalysisPeriod | None]
        if not self.ready:
            return None, None, None

        # --------------------------------------------------------------------------------------------------------------
        # -- Load in the STAT and EPW files
        lb_epw = EPW(self.epw_file)
        lb_stat = STAT(self.sat_file)
        winter_outage_period, winter_outage_period_expanded = self.check_extreme_week(lb_stat.extreme_cold_week)
        summer_outage_period, summer_outage_period_expanded = self.check_extreme_week(lb_stat.extreme_hot_week)

        # --------------------------------------------------------------------------------------------------------------
        # -- Pull out the STAT file's Peak Winter and Peak Summer Weeks from the Ladybug EPW file
        dry_bulb_deg_C = lb_epw.dry_bulb_temperature  # type: HourlyContinuousCollection
        dew_point_deg_C = lb_epw.dew_point_temperature  # type: HourlyContinuousCollection

        # --------------------------------------------------------------------------------------------------------------
        # -- Slice out the analysis period data from the EPW
        winter_dry_bulb_deg_C = self.filter_by_analysis_period(dry_bulb_deg_C, winter_outage_period)
        winter_dew_point_deg_C = self.filter_by_analysis_period(dew_point_deg_C, winter_outage_period)

        summer_dry_bulb_deg_C = self.filter_by_analysis_period(dry_bulb_deg_C, summer_outage_period)
        summer_dew_point_deg_C = self.filter_by_analysis_period(dew_point_deg_C, summer_outage_period)

        # --------------------------------------------------------------------------------------------------------------
        # -- Calculate the Phius-REVIVE Weather-Morphing Factors
        # -- Adapted from https://github.com/Phius-ResearchComittee/REVIVE/blob/main/REVIVE2024/weatherMorph.py
        iters, winter_dry_bulb_factor = calculate_adjustment_factor(
            self.winter_10yr_dry_bulb_C, winter_dry_bulb_deg_C, min
        )
        print("Winter Dry-Bulb Factor: {:,.3f} (took {} iterations)".format(winter_dry_bulb_factor, iters))

        iters, winter_dew_point_factor = calculate_adjustment_factor(
            self.winter_10yr_dew_point_C, winter_dew_point_deg_C, min
        )
        print("Winter Dew-Point Factor: {:,.3f} (took {} iterations)".format(winter_dew_point_factor, iters))

        iters, summer_dry_bulb_factor = calculate_adjustment_factor(
            self.summer_20yr_dry_bulb_C, summer_dry_bulb_deg_C, max
        )
        print("Summer Dry-Bulb Factor: {:,.3f} (took {} iterations)".format(summer_dry_bulb_factor, iters))

        iters, summer_dew_point_factor = calculate_adjustment_factor(
            self.summer_20yr_dew_point_C, summer_dew_point_deg_C, max
        )
        print("Summer Dew-Point Factor: {:,.3f} (took {} iterations)".format(summer_dew_point_factor, iters))

        # --------------------------------------------------------------------------------------------------------------
        # -- Generate a new EPW with the factors applied to the data
        new_epw = copy(lb_epw)
        new_epw._data[6] = apply_adjustment_factor_to_epw_data(
            new_epw.dry_bulb_temperature, winter_dry_bulb_deg_C, winter_outage_period, winter_dry_bulb_factor
        )
        new_epw._data[6] = apply_adjustment_factor_to_epw_data(
            new_epw.dry_bulb_temperature, summer_dry_bulb_deg_C, summer_outage_period, summer_dry_bulb_factor
        )
        new_epw._data[7] = apply_adjustment_factor_to_epw_data(
            new_epw.dew_point_temperature, winter_dew_point_deg_C, winter_outage_period, winter_dew_point_factor
        )
        new_epw._data[7] = apply_adjustment_factor_to_epw_data(
            new_epw.dew_point_temperature, summer_dew_point_deg_C, summer_outage_period, summer_dew_point_factor
        )

        # --------------------------------------------------------------------------------------------------------------
        # -- Check the dew-points to make sure they are never higher than the dry-bulb
        new_epw._data[7] = check_dew_point_temperature(
            new_epw.dew_point_temperature,
            new_epw.dry_bulb_temperature,
        )

        # --------------------------------------------------------------------------------------------------------------
        # -- Save the new EPW file to disk
        _file_name_ = "Phius_REVIVE_2024_{}".format(os.path.basename(str(new_epw.file_path)))
        epw_filepath_ = os.path.join(self.folder, _file_name_)
        new_epw.save(epw_filepath_)

        return epw_filepath_, winter_outage_period_expanded, summer_outage_period_expanded
