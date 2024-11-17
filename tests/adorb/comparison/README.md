# ADORB TEST MODEL COMPARISON:

Below is a comparison of two EnergyPlus simulations: one simulation using the [KMR Example model](https://github.com/Phius-ResearchComittee/REVIVE/releases/tag/v24.2.0) provided by Phius, run using their Phius-REVIVE GUI tool, and another using a [Honeybee-REVIVE model](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_model.hbjson) which was built to match the KMR example as closely as possible using Honeybee Grasshopper methods and components. The test model is a single-zone, single-family home. The home includes a below-grade basement, as well as two on-grade floor surfaces ("Crawlspace" and "Slab"):

![Screenshot 2024-11-10 at 1 54 14 PM](https://github.com/user-attachments/assets/16ee8959-04b4-4815-8975-660c6f56d87b)

# METHODOLOGY:
Using the [Honeybee-REVIVE toolkit](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main), a complete Honeybee-REVIVE model was constructed in Rhino/Grasshopper with attributes which align to the Phius KMR Example file as closely as possible (see below for a discussion of the known discrepancies). A full annual simulation was executed for both simulations, and the ADORB costs calculated based on the simulation results. ADORB costs for the Phius-case were calculated using their Phius-GUI tool, while the HB-REVIVE case uses the new [PH-ADORB library](https://github.com/PH-Tools/PH_ADORB).

### MODEL FILES:
Relevant model files can be found at:
- [EPW File: Rochester, MN](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/_source_weather/USA_MN_Rochester.Intl.AP.726440_TMY3)
- - -
- [Phius GUI Generated IDF](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/adorb/phius_gui)
- [Phius GUI Generated Results](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/adorb/phius_gui/results)
- - - 
- [Grasshopper Model Generation Script](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_model.gh)
- [Grasshopper Simulation Run Script](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_simulate_ADORB.gh)
- [Honeybee-REVIVE Model Results](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/adorb/hbrv/hb_revive_ADORB_results)


### KNOWN MODEL DIFFERENCES:
There are four key discrepancies found between the Honeybee-REVIVE model and the Phius-GUI model which have been identified during this comparison:
1. **Kiva:** The Phius GUI utilizes the [KIVA ground solver](https://kiva.readthedocs.io/en/stable/), while the Honeybee model does not. This feature is not currently supported by Honeybee. For the purposes of this evaluation, a temporary 'patch' was applied to the Honeybee model in order to enable KIVA in both simulations. In the long term, Honeybee would need to provide feature support for KIVA in order to allow alignment with the REVIVE protocol. While there does not appear to be significant difference when the model uses well insulated surfaces, for models which have un- or poorly-insulated ground-contact surfaces (typical of many existing homes) there does appear to a large difference in modeled performance when Kiva is used.
1. **Mechanical Equipment:** The Phius-GUI tool uses 'hard-coded' mechanical equipment for a [selection of different types](https://github.com/Phius-ResearchComittee/REVIVE/blob/5ddd9cc7f55639071ac35f9b1701c286b68b1ca6/REVIVE2024/hvac.py#L106) common in smaller residential buildings. By contrast, the Honeybee-REVIVE model is restricted to only the mechanical systems available through [NREL's OpenStudio Standards templates.](https://github.com/NREL/openstudio-standards) While these templates are quite comprehensive, they do not have an option that matches the Phius-GUI system perfectly, and so there is some inevitable discrepancy between the model's mechanical equipment. </br></br>
*Note: while it does appear possible to configure a detailed system for the Honeybee-REVIVE model using the [IronBug](https://github.com/MingboPeng/Ironbug) plugin, this plugin is not currently available for MacOS or Windows-ARM systems and so was not tested as part of this validation testing. Further testing on a Windows-OS may show better alignment between systems if IronBug is used.*</br></br>
1. **Envelope Infiltration Parameters:** While both models have the same infiltration flow-rate, the Phius-GUI and Honeybee set different attributes for the `Temperature Term Coefficient` and `Velocity Term Coefficient` values in the EnergyPlus IDF `ZoneInfiltration:DesignFlowRate` object. For purposes of this study, the Honeybee-REVIVE IDF values were patched to match the Phius-GUI settings in order to align the simulation results. 
1. **Maintenance and Replacement Cost:** There appears to be an error [in the Phius-GUI code](https://github.com/Phius-ResearchComittee/REVIVE/blob/5ddd9cc7f55639071ac35f9b1701c286b68b1ca6/REVIVE2024/simulate.py#L1067) which causes all model construction material costs to be duplicated on year 1, leading to an erroneously high ADORB cost. The error is fixed in the Honeybee-REVIVE implementation, and as a result the maintenance and replacement ADORB cost is 50% lower in the Honeybee-REVIVE case.
1. **Mechanical Ventilation:** While the Phius-GUI case does include a specified fresh-air-ventilation flow rate, the test-case mechanical system with "Exhaust" ventilation does not include any Mixers in the IDF, and therefor does there is '0' ventilation airflow to the 'Furnace'. In order to match this effect, since the NREL templates cannot be modified to perfectly match this configuration, the ventilation flow-rate in the Honeybee-REVIVE model have been set to '0'. This has the same effect of zeroing out the mechanical ventilation airflow to the heating/cooling coils.
</br></br>


# ENERGYPLUS SIMULATION RESULTS:

<details>
<summary><strong>Site Outdoor Conditions:</strong></summary>

As shown, the outdoor boundary conditions for both simulations are identical. Both simulation runs use EPW data from [Rochester, MN.](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/_source_weather/USA_MN_Rochester.Intl.AP.726440_TMY3)

![Screenshot](./energy_plus/png/site_outdoor_air_drybulb_temperature.png)
![Screenshot](./energy_plus/png/site_outdoor_air_relative_humidity.png)
![Screenshot](./energy_plus/png/site_outdoor_air_wetbulb_temperature.png)

</details>

<details>
<summary><strong>Zone Indoor Conditions:</strong></summary>

The simulated interior air conditions of both simulations show good alignment across both summer and winter. As a result of differences in the mechanical system components, the Phius-GUI model does show slightly warmer interior temperatures, and as a result also slightly less humid conditions through the year. It is not clear where this difference derives from, but it is small enough that we do not feel it affects the final results in a significant way. This may be area for further testing and analysis to determine what is causing this difference. 

![Screenshot](./energy_plus/png/zone_mean_air_temperature.png)
![Screenshot](./energy_plus/png/zone_air_relative_humidity.png)

</details>

<details>
<summary><strong>Zone Internal Gains:</strong></summary>

Lighting, Occupancy, and Appliances follow the same pattern in both the Phius-GUI and Honeybee-REVIVE models. One notable difference is that Honeybee-REVIVE models all of the appliances as 'OtherEquipment', rather than "ElectricEquipment" which makes direct comparison challenging.

![Screenshot](./energy_plus/png/zone_lights_electricity_energy.png)
![Screenshot](./energy_plus/png/zone_people_total_heating_energy.png)
![Screenshot](./energy_plus/png/zone_electric_equipment_electricity_energy.png)

</details>

<details>
<summary><strong>Zone Ventilation Airflows:</strong></summary>

Airflows for Mechanical, Infiltration, and Windows are aligned across both models. Note that the Phius test case uses a 'Exhaust' only ventilation configuration and therefor the Mechanical Ventilation is zero'd out. 

![Screenshot](./energy_plus/png/zone_mechanical_ventilation_standard_density_volume_flow_rate.png)
![Screenshot](./energy_plus/png/zone_infiltration_standard_density_volume_flow_rate.png)
![Screenshot](./energy_plus/png/zone_ventilation_standard_density_volume_flow_rate.png)

</details>

<details>
<summary><strong>Heating and Cooling Energy:</strong></summary>

As shown, the models show good alignment for heating and cooling energy consumption during both summer and winter. As noted above, the Honeybee-REVIVE model does appear to have slightly higher summertime temperatures, amd slightly lower cooling energy consumption. This may be the result of a sensor or thermostat configuration and may be a place for further refinement and study. However, the difference appears to be minor and does not significantly affect the final ADORB calculation results. 

![Screenshot](./energy_plus/png/heating_coil_natural_gas_energy.png)
![Screenshot](./energy_plus/png/cooling_coil_electricity_energy.png)


</details>

</br></br>

# ADORB COST RESULTS:
Below is a summary of the ADORB cost values calculated for both the Phius-GUI model as well as the Honeybee-REVIVE model. 


## Operational Energy Purchase PV-Cost:
These costs represent the present-value of future net energy purchasing costs. There is good alignment between the modeled cases, with the Phius-GUI simulations showing a slightly higher rate due to its slightly higher simulated energy consumption. 

![Screenshot](./adorb_cost/png/energy_purchase_cost.png)

## Operational Energy CO2 PV-Cost:
These costs represent the present-value of CO2-emissions costs of all future net energy consumption.

![Screenshot](./adorb_cost/png/energy_CO2_cost.png)


## Construction Measure Purchase PV-Cost:
These costs represent the present-value of all 'construction' related expenses including all relevant materials, equipment, products, and other 'measures' which are taken during the life of the building which affect the carbon-emissions and the out-of-pocket costs. These costs include all first-costs associated with the acquisition (material) and installation (labor) as well as all recurring maintenance and replacement costs.

![Screenshot](./adorb_cost/png/construction_purchase_cost.png)


## Construction Measure CO2 PV-Cost:
These cost represent the present-value of all 'construction' related embodied CO2 emissions costs. This includes all ongoing maintenance and replacement costs. 

![Screenshot](./adorb_cost/png/construction_CO2_cost.png)


## Grid Transition PV-Cost:
These costs represent the present-value of a recurring 'grid-transition' fee which covers the increased electrical load of the building as it transitions from fossil-fuels to all electric heating and cooling. This would be equivalent to a tax levied on the property directly supporting the national grid transition costs. Note that after 30 years the cost goes to zero as the transition is assumed to be complete at that point.

While there is alignment between the two simulations, it is notable that the year-0 costs calculated by the Phius-GUI are 2x the Honeybee-REVIVE values. This owing to an error in the Phius-GUI calculation methodology where the building's constructions are added twice at year-0. Once this error is fixed the results will align for all years.

![Screenshot](./adorb_cost/png/grid_transition_cost.png)


## Total Cumulative ADORB Cost:
Looking at the total Cumulative ADORB costs over the analysis period

