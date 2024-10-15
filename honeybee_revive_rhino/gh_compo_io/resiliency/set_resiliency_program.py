# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Resiliency Program."""

import os

try:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.dt import Date, DateTime
except ImportError as e:
    raise ImportError("\nFailed to import ladybug: {0}".format(e))

try:
    from honeybee.room import Room
    from honeybee.model import Model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee: {0}".format(e))

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.properties.room import RoomEnergyProperties
    from honeybee_energy.load.process import Process
except ImportError:
    raise ImportError("\nFailed to import honeybee_energy")

try:
    import honeybee_revive_standards
    from honeybee_revive_rhino.gh_compo_io.standards._load import (
        load_program_and_schedules,
        load_schedules_from_standards,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive_rhino: {0}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units: {0}".format(e))


class GHCompo_SetResiliencyProgram(object):
    num_dwellings = validators.IntegerNonZero("num_dwellings")
    DEFAULT_PROGRAM_NAME = "rv2024_Residence_Resilience"

    def __init__(
        self, _IGH, _hb_obj, _num_dwellings, _elec_equip, _program, _winter_period, _summer_period, *args, **kwargs
    ):
        # type: (gh_io.IGH, list[Room | Model], int, list[Process], ProgramType | None, AnalysisPeriod, AnalysisPeriod, list, dict) -> None
        self.IGH = _IGH
        self.model = None  # type: Model | None
        self.rooms = _hb_obj
        self.num_dwellings = _num_dwellings
        self.elec_equip = _elec_equip
        self.program = _program
        self.winter_period = _winter_period
        self.summer_period = _summer_period

    @property
    def rooms(self):
        # type: () -> list[Room]
        return self._rooms

    @rooms.setter
    def rooms(self, _input):
        # type: (list[Room | Model]) -> None
        self._rooms = []
        for item in _input:
            if isinstance(item, Room):
                self._rooms.append(item)
            elif isinstance(item, Model):
                self._rooms.extend(item.rooms)
                self.model = item

    @property
    def standards_dir(self):
        # type: () -> str
        return os.path.dirname(honeybee_revive_standards.__file__)

    @property
    def ready(self):
        # type: () -> bool
        if self.num_dwellings is None:
            return False
        if len(self.rooms) == 0:
            return False
        if not self.winter_period or not self.summer_period:
            return False
        return True

    def run(self):
        # type: () -> tuple[list[Room] | Model, ProgramType | None]
        if not self.ready:
            return ([], None)

        # --------------------------------------------------------------------------------------------------------------
        # -- Get the Residential Resiliency Program to use
        if not self.program:
            print("Loading the '{}' program from standards.".format(self.DEFAULT_PROGRAM_NAME))
            rv2024_resilience_program = load_program_and_schedules(self.standards_dir, self.DEFAULT_PROGRAM_NAME)
        else:
            rv2024_resilience_program = self.program.duplicate()

        if not rv2024_resilience_program:
            self.IGH.error("Failed to load a Residential Resiliency program?")
            return ([], None)

        rv2024_resilience_program.unlock()

        # --------------------------------------------------------------------------------------------------------------
        # -- Figure out the total occupancy, MEL, Ventilation for the rooms
        total_floor_area_rh_units = sum(rm.floor_area for rm in self.rooms)
        total_floor_area_m2 = convert(total_floor_area_rh_units, self.IGH.get_rhino_areas_unit_name(), "M2") or 0.0
        print("Total floor area: {:,.1f} m2".format(total_floor_area_m2))

        if total_floor_area_rh_units == 0:
            self.IGH.error("Total floor area is zero. Please make sure the rooms have valid floor surfaces?")
            return ([], None)

        # -- Occupancy to match the Room's existing occupancy load
        total_occupancy = 0.0
        for rm in self.rooms:
            rm_area_m2 = convert(rm.floor_area, self.IGH.get_rhino_areas_unit_name(), "M2") or 0.0
            if rm_area_m2 is None:
                self.IGH.warning("Failed to convert room's floor area to M2: {}".format(rm.floor_area))
                continue
            rm_energy_prop = getattr(rm.properties, "energy")  # type: RoomEnergyProperties
            total_occupancy += rm_energy_prop.people.people_per_area * rm_area_m2

        # -- Infiltration rate to math the Room's existing infiltration load
        total_infiltration_m3_s = 0.0
        total_exposed_area_m2 = 0.0
        for rm in self.rooms:
            rm_exposed_area_m2 = convert(rm.exposed_area, self.IGH.get_rhino_areas_unit_name(), "M2") or 0.0
            if rm_exposed_area_m2 is None:
                self.IGH.warning("Failed to convert room's exposed-area to M2: {}".format(rm.floor_area))
                continue
            rm_energy_prop = getattr(rm.properties, "energy")
            total_infiltration_m3_s += rm_energy_prop.infiltration.flow_per_exterior_area * rm_exposed_area_m2
            total_exposed_area_m2 += rm_exposed_area_m2
        infiltration_per_exposed_area = total_infiltration_m3_s / total_exposed_area_m2

        # -- Set 33-W per dwelling as per Phius REVIVE Rules (=1 fridge)
        total_MEL_wattage = self.num_dwellings * 33.0
        for equip in self.elec_equip:
            total_MEL_wattage += equip.watts

        # -- Set 5-CFM per person as per Phius REVIVE Rules
        total_vent_cfm = total_occupancy * 5
        total_vent_m3s = convert(total_vent_cfm, "CFM", "M3/S") or 0.0
        vent_m3s_per_person = total_vent_m3s / total_occupancy

        # TODO: Add in the _additional_elec_equip....

        # --------------------------------------------------------------------------------------------------------------
        # -- Re-Set the Program's Occupancy, MEL, Ventilation
        # TODO: Q - Should we be preserving the room-level occupancy diversity? hmm....
        ppl_per_area = total_occupancy / total_floor_area_m2
        print("Setting Occupancy load to: {:,.1f} ppl [{:.4f} ppl/m2]".format(total_occupancy, ppl_per_area))
        rv2024_resilience_program.people.people_per_area = ppl_per_area

        mel_per_area = total_MEL_wattage / total_floor_area_m2
        print("Setting MEL load to: {:,.1f} W [{:.4f} W/m2]".format(total_MEL_wattage, mel_per_area))
        rv2024_resilience_program.electric_equipment.watts_per_area = mel_per_area

        print("Setting Vent. load to: {:,.1f} CFM [{:.4f} m3s/person]".format(total_vent_cfm, vent_m3s_per_person))
        rv2024_resilience_program.ventilation.flow_per_person = vent_m3s_per_person

        print("Setting Infiltration load to: {:,.6f} m3/s".format(infiltration_per_exposed_area))
        rv2024_resilience_program.infiltration.flow_per_exterior_area = infiltration_per_exposed_area

        # --------------------------------------------------------------------------------------------------------------
        # -- Create the Setpoint Schedules based on the Winter and Summer Periods
        print("Setting the Setpoint Schedules based on the Winter and Summer Periods.")
        schedules_dict = load_schedules_from_standards(self.standards_dir)
        heating_off_schedule = schedules_dict["rv2024_HeatingOff"]
        cooling_off_schedule = schedules_dict["rv2024_CoolingOff"]
        humid_off_schedule = schedules_dict["rv2024_HumidificationOff"]
        dehumid_off_schedule = schedules_dict["rv2024_DehumidificationOff"]

        # -- NOTE: Be sure to clip off a day on either end of the analysis period.
        # -- Heating and Humidification Schedules 'OFF' during outage
        htg_start = Date.from_doy(DateTime.from_hoy(self.winter_period.st_time.hoy + 24).doy)
        htg_end = Date.from_doy(DateTime.from_hoy(self.winter_period.end_time.hoy - 24).doy)
        for heating_rule in heating_off_schedule.to_rules(htg_start, htg_end):
            rv2024_resilience_program.setpoint.heating_schedule.add_rule(heating_rule)
        for humid_rule in humid_off_schedule.to_rules(htg_start, htg_end):
            rv2024_resilience_program.setpoint.humidifying_schedule.add_rule(humid_rule)

        # -- Cooling and Dehumidification Schedules 'OFF' during outage
        clg_start = DateTime.from_hoy(self.summer_period.st_time.hoy + 24).date
        clg_end = DateTime.from_hoy(self.summer_period.end_time.hoy - 24).date
        for cooling_rule in cooling_off_schedule.to_rules(clg_start, clg_end):
            rv2024_resilience_program.setpoint.cooling_schedule.add_rule(cooling_rule)
        for dehumid_rule in dehumid_off_schedule.to_rules(clg_start, clg_end):
            rv2024_resilience_program.setpoint.dehumidifying_schedule.add_rule(dehumid_rule)

        # --------------------------------------------------------------------------------------------------------------
        rv2024_resilience_program.lock()

        # --------------------------------------------------------------------------------------------------------------
        # -- Set all the Room's Programs

        new_rooms_ = []
        for room in self.rooms:
            new_room = room.duplicate()
            new_rm_energy_prop = getattr(new_room.properties, "energy")  # type: RoomEnergyProperties
            new_rm_energy_prop.program_type = rv2024_resilience_program
            new_rm_energy_prop.reset_loads_to_program()
            new_rooms_.append(new_room)

        # --------------------------------------------------------------------------------------------------------------
        # -- If the input was a Model, output a Model, otherwise output a list of Rooms
        if not self.model:
            hb_obj_ = new_rooms_
        else:
            new_model = self.model.duplicate()
            new_model._rooms = new_rooms_
            hb_obj_ = new_model

        return hb_obj_, rv2024_resilience_program
