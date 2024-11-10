Below is a comparison of two EnergyPlus simulation models: one done using the [KMR Example model](https://github.com/Phius-ResearchComittee/REVIVE/releases/tag/v24.2.0) provided by Phius and the Phius GUI tool, and another using a [Honeybee-REVIVE model](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_model.hbjson) which was built to match the KMR example as closely as possible using Honeybee Grasshopper methods and components. The test model is a single-zone, single-family home. The home includes a below-grade basement, as well as two on-grade floor surfaces ("Crawlspace" and "Slab"):

![Screenshot 2024-11-10 at 1 54 14 PM](https://github.com/user-attachments/assets/16ee8959-04b4-4815-8975-660c6f56d87b)


# METHODOLOGY:
Using the [Honeybee-REVIVE toolkit](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main), a complete Honeybee model was constructed in Rhino/Grasshopper with attributes which align to the Phius KMR Example file. Resiliency 'peak-week' simulations were carried out for both the 'Phius-GUI' generated case(s) and the Honeybee-REVIVE cases for both the winter and summer resiliency assessment periods as defined in the climate STAT files (extreme hot and extreme cold week). Note that the default Phius-GUI generated files were modified to adjust their RunPeriod and limited to these extreme weeks only, rather than simulating the entire year.

### MODEL FILES:
Relevant model files can be found at:
- [WINTER | Phius GUI Generated IDF](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/resilience/winter/phius_gui)
- [SUMMER | Phius GUI Generated IDF](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/resilience/summer/phius_gui)
- - - 
- [Rhino/Grasshopper Model](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_model.gh)
- [Rhino/Grasshopper Simulation Run](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_simulate_resiliency.gh)
- [Honeybee-REVIVE HBJSON Model](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/blob/main/tests/phius_rv2024_model.hbjson)
- - - 
- [WINTER | Honeybee-REVIVE Outputs](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/resilience/winter/hbrv)
- [SUMMER | Honeybee-REVIVE Outputs](https://github.com/PH-Tools/honeybee_REVIVE_grasshopper/tree/main/tests/resilience/summer/hbrv)


### KNOWN MODEL DIFFERENCES:
There are three key discrepancies between the basic Honeybee model and the Phius-GUI model:
1. **Kiva:** The Phius GUI utilizes the KIVA ground solver, while the Honeybee model does not. This feature is not currently supported by Honeybee. For the purposes of this evaluation, a temporary 'patch' was applied to the Honeybee model in order to enable KIVA in both simulations. In the long term, Honeybee would need to provide feature support for KIVA in order to allow alignment with the REVIVE protocol.
1. **People:** In order to output SET temperatures from EnergyPlus, the 'People' object must have its 'Thermal Comfort Model' set to the 'Pierce' option. This feature is not currently supported in Honeybee. For the purposes of this evaluation, a temporary patch was applied using an EnergyPlus "Measure". This solution is not generalizable to other models however, and full feature support for these Thermal Comfort Models would need to be added to Honeybee in order to allow alignment with the REVIVE protocol.
1. **Weather:** The simulation methods use a different approach to the weather files. The Phius GUI tool implements [a method](https://github.com/Phius-ResearchComittee/REVIVE/blob/5ddd9cc7f55639071ac35f9b1701c286b68b1ca6/REVIVE2024/weatherMorph.py#L45) which utilizes run-time EMS scripts to modify the outdoor dry-bulb and dew-point temperatures. By contrast, the Honeybee-REVIVE tool uses a [pre-processor method](https://github.com/PH-Tools/honeybee_REVIVE/blob/40c9aa9b0d11c579753599f9ba332e4daa812355/ladybug_revive/resiliency_epw.py#L116) to generate modified EPW weather files. This difference in methodology results in some very minor differences (+/- 0.1°C) in places.

Detailed comparisons are shown below:


# WINTER RESULTS:


<details>
<summary><strong>Indoor Environment</strong></summary>

As shown below, the Phius-GUI generated model and the Honeybee-Generated model show very close alignment across the key interior air properties: Dry-Bulb temp, Relative Humidity, and SET Comfort Temperature. The Honeybee model does show a slightly lower air temp, which causes a corresponding drop in the SET temperatures as well. This is likely due to the increased infiltration rate (see below).
![Winter Internal Conditions](https://github.com/user-attachments/assets/507726c3-bc38-4d3e-86b3-b224fae2a736)
</details>

<details>
<summary><strong>Outdoor Environment</strong></summary>

Both simulations show alignment in the outdoor air environment used. Note that there is some small deviation as a result of the different methods used to generate these outdoor air boundary conditions: The Phius GUI uses a runtime EMS script to modify the outdoor air conditions during the EnergyPlus simulation, while the Honeybee-REVIVE tool uses a pre-processor to generate modified EPW files. These methods will inevitable lead to small variations (+/-0.1°C)
![Winter Outdoor Conditions](https://github.com/user-attachments/assets/3c128c2d-2ea0-4d4d-bea0-8d47f14b1595)
</details>


<details>
<summary><strong>Internal Gains</strong></summary>

Internal Gains for people, lighting, and electrical-equipment are aligned between models. Note the small variation in electrical energy: the Phius rules state that we should use 33W continuous to approximate a refrigerator, however the Phius GUI does not follow this rule and instead uses a 44W refrigerator. This discrepancy (10W) is not significant and does not affect the outputs in any meaningful way.
![Winter Internal Heat Gains](https://github.com/user-attachments/assets/ac9ef237-aa64-4ff5-a600-9a9811865228)
</details>


<details>
<summary><strong>Window Gain / Loss</strong></summary>

Window solar gain and heat loss show good alignment between simulations. The window surfaces and constructions are aligned across both simulations, so any variation in heat-gain/heat-loss observed is due to variations in indoor air conditions. The differences observed are minor, where they occur.
![Winter Windows](https://github.com/user-attachments/assets/fbd449b6-0397-42cd-9b07-847d5e6af286)
</details>

<details>
<summary><strong>Ventilation Airflow</strong></summary>

While Mechanical Ventilation and 'Ventilation' (windows) show alignment across both simulations, the infiltration ventilation shows a non-trivial difference. This difference is owing to the different configuration and calculation modes used by the two simulation tools:

While the Phius GUI tool sets values for the 'Temperature Turn Coefficient' and the 'Velocity Term Coefficient' to 0.015 and 0.224 (respectively), the Honeybee simulation leaves these values at the default value of 0. This difference in the calculation parameters accounts for the difference in resulting total infiltration flow rate. These values are not configurable in the Honeybee simulation without using a Measure or other workaround. Owing to the relatively small impact on the overall energy/comfort performance, it is proposed to leave these values different. 
![Screenshot 2024-11-10 at 1 40 40 PM](https://github.com/user-attachments/assets/38e3113d-2f42-4b92-8849-0062d8015872)

![Winter Ventilation](https://github.com/user-attachments/assets/8bce4f48-3aed-43e3-a592-3d6d12c63ab9)
</details>

</br>

# SUMMER RESULTS:

<details>
<summary><strong>Indoor Environment</strong></summary>

As shown below, the Phius-GUI generated model and the Honeybee-Generated model show very close alignment across the key summer-resiliency interior air properties: Dry-Bulb temp, Relative Humidity, and Heat Index. The Honeybee model does show a slightly higher air temp, which causes a corresponding difference in the Heat Index values as well. This is likely due to the increased infiltration rate (see below) of the Honeybee-REVIVE model relative to the Phius-GUI model.
![Summer Interior Conditions](https://github.com/user-attachments/assets/c5b8a6e7-613c-430e-abce-9ce827ba4e0e)
</details>

<details>
<summary><strong>Outdoor Environment</strong></summary>

Both simulations show alignment in the outdoor air environment used.
![Summer Outdoor Conditions](https://github.com/user-attachments/assets/7416e77e-5cd6-48a9-ba03-60739cb2b90b)
</details>


<details>
<summary><strong>Internal Gains</strong></summary>

Internal Gains for people, lighting, and electrical-equipment are aligned between models. Note the small variation in electrical energy: the Phius rules state that we should use 33W continuous to approximate a refrigerator, however the Phius GUI does not follow this rule and instead uses a 44W refrigerator. This discrepancy (10W) is not significant and does not affect the outputs in any meaningful way.
![Summer Internal Heat Gains](https://github.com/user-attachments/assets/4a1c8df0-5644-4011-bf36-971257a20c0d)
</details>


<details>
<summary><strong>Window Gain / Loss</strong></summary>

Window solar gain and heat loss show good alignment between simulations. The window surfaces and constructions are aligned across both simulations, so any variation in heat-gain/heat-loss observed is due to variations in indoor air conditions. The differences observed are minor, where they occur.
![Summer Windows](https://github.com/user-attachments/assets/955746a6-ae0a-40ad-a911-7e5ca5948ffd)
</details>

<details>
<summary><strong>Ventilation Airflow</strong></summary>

As discussed in the 'Winter Ventilation Airflow' section above, the simulations utilize different calculation parameters for infiltration airflow, and as a result the Honeybee-REVIVE model shows considerably more infiltration than the Phius-GUI. 'Mechanical Ventilation' and 'Ventilation' (windows) show good alignment between both simulations however.

![Summer Ventilation](https://github.com/user-attachments/assets/ba04963b-e0b2-4204-bd6a-726c4846e1a3)
</details>
