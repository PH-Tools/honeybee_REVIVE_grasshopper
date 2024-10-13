# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Resiliency Simulation Output Variables."""

try:
    from honeybee_energy.simulation.output import SimulationOutput
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_SetResiliencySimulationOutputVariables(object):
    resiliency_simulation_outputs = [
        "Zone Thermal Comfort Pierce Model Standard Effective Temperature",
        "Zone Air Relative Humidity",
        "Zone Mean Air Temperature",
        "Zone Mean Radiant Temperature",
        "Site Outdoor Air Drybulb Temperature",
        "Site Outdoor Air Dewpoint Temperature",
        "Site Outdoor Air Wetbulb Temperature",
        "Site Outdoor Air Humidity Ratio",
        "Site Outdoor Air Relative Humidity",
    ]

    def __init__(self, _IGH, _sim_output):
        # type: (gh_io.IGH, SimulationOutput | None) -> None
        self.IGH = _IGH
        self.sim_output = _sim_output

    def run(self):
        # type: () -> SimulationOutput
        sim_output = self.sim_output.duplicate() if self.sim_output is not None else SimulationOutput()
        sim_output.reporting_frequency = "Hourly"
        for output_name in self.resiliency_simulation_outputs:
            sim_output.add_output(output_name)
        return sim_output
