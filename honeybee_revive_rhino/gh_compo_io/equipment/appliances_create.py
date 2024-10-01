# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create REVIVE Appliance."""

try:
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.load.process import Process
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


class GHCompo_CreateReviveAppliance(object):

    def __init__(
        self,
        _IGH,
        _name,
        _watts,
        _schedule,
        _fuel_type,
        _use_category,
        _radiant_fraction,
        _latent_fraction,
        _lost_fraction,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, float, str | ScheduleRuleset, str, str, float, float, float, list, dict) -> None
        self.IGH = _IGH
        self.name = _name
        self.watts = _watts or 0.0
        self.schedule = _schedule
        self.fuel_type = _fuel_type or "Electricity"
        self.use_category = _use_category or "Process"
        self.radiant_fraction = _radiant_fraction or 0.0
        self.latent_fraction = _latent_fraction or 0.0
        self.lost_fraction = _lost_fraction or 0.0

    @property
    def name(self):
        # type: () -> str
        return self._name

    @name.setter
    def name(self, _input):
        # type: (str) -> None
        if not _input:
            self._name = clean_and_id_ep_string("Process")
        else:
            self._name = clean_ep_string(_input)

    @property
    def schedule(self):
        # type: () -> ScheduleRuleset | ScheduleFixedInterval
        return self._schedule

    @schedule.setter
    def schedule(self, _input):
        # type: (str | ScheduleRuleset) -> None
        if isinstance(_input, str):
            found_schedule = schedule_by_identifier(_input)
            if not found_schedule:
                raise ValueError("Failed to find a schedule with the identifier: {}".format(_input))
            else:
                self._schedule = found_schedule
        else:
            self._schedule = _input

    def run(self):
        # type: () -> Process | None
        if not self.schedule:
            return None

        return Process(
            self.name,
            self.watts,
            self.schedule,
            self.fuel_type,
            self.use_category,
            self.radiant_fraction,  # type: ignore
            self.latent_fraction,  # type: ignore
            self.lost_fraction,  # type: ignore
        )
