## METHODOLOGY:

Below is a comparison of two simulation models: one done using the KMR Example model and the Phius GUI tool, and another using a Honeybee-REVIVE model which was built to match the KMR example as closely as possible using Honeybee Grasshopper methods and components. The model is a single-zone single-family home:


### 
Kiva
People



## RESULTS:

As shown below, the Phius-GUI generated model and the Honeybee-Generated model show very close alignment across the key interior air properties: Dry-Bulb temp, Relative Humidity, and SET Comfort Temperature. The Honeybee model does show a slightly lower air temp, which causes a corresponding drop in the SET temperatures as well. This is likely due to the increased infiltration rate (see below).
![Internal Conditions](https://github.com/user-attachments/assets/507726c3-bc38-4d3e-86b3-b224fae2a736)

- - - 
<details>
<summary><strong>Outdoor Environment</strong></summary>

Both simulations show alignment in the outdoor air environment used. Note that there is some small deviation as a result of the different methods used to generate these outdoor air boundary conditions: The Phius GUI uses a runtime EMS script to modify the outdoor air conditions during the EnergyPlus simulation, while the Honeybee-REVIVE tool uses a pre-processor to generate modified EPW files. These methods will inevitable lead to small variations (+/-0.1°C)
![Outdoor Conditions](https://github.com/user-attachments/assets/3c128c2d-2ea0-4d4d-bea0-8d47f14b1595)
</details>

- - - 
<details>
<summary><strong>Internal Gains</strong></summary>

Internal Gains for people, lighting, and electrical-equipment are aligned between models. Note the small variation in electrical energy: the Phius rules state that we should use 33W continuous to approximate a refrigerator, however the Phius GUI does not follow this rule and instead uses a 44W refrigerator. This discrepancy (10W) is not significant and does not affect the outputs in any meaningful way.
![Internal Heat Gains](https://github.com/user-attachments/assets/ac9ef237-aa64-4ff5-a600-9a9811865228)
</details>


- - -
<details>
<summary><strong>Window Gain / Loss</strong></summary>

Window solar gain and heat loss show good alignment between simulations. The window surfaces and constructions are aligned across both simulations, so any variation in heat-gain/heat-loss observed is due to variations in indoor air conditions. The differences observed are minor, where they occur.
![Windows](https://github.com/user-attachments/assets/fbd449b6-0397-42cd-9b07-847d5e6af286)
</details>

- - - 
<details>
<summary><strong>Ventilation Airflow</strong></summary>

While Mechanical Ventilation and 'Ventilation' (windows) show alignment across both simulations, the infiltration ventilation shows a non-trivial difference. This difference is owing to the different configuration and calculation modes used by the two simulation tools:

While the Phius GUI tool sets values for the 'Temperature Turn Coefficient' and the 'Velocity Term Coefficient' to 0.015 and 0.224 (respectively), the Honeybee simulation leaves these values at the default value of 0. This difference in the calculation parameters accounts for the difference in resulting total infiltration flow rate. These values are not configurable in the Honeybee simulation without using a Measure or other workaround. Owing to the relatively small impact on the overall energy/comfort performance, it is proposed to leave these values different. 
![Screenshot 2024-11-10 at 1 40 40 PM](https://github.com/user-attachments/assets/38e3113d-2f42-4b92-8849-0062d8015872)

![Ventilation](https://github.com/user-attachments/assets/8bce4f48-3aed-43e3-a592-3d6d12c63ab9)
</details>
