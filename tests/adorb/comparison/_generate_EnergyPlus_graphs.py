import sqlite3
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go


def get_from_sql(_source_file_path) -> dict:
    """Get the 'Facility Total Building Electricity Demand Rate' [W] from the SQL File."""
    conn = sqlite3.connect(_source_file_path)
    try:
        c = conn.cursor()
        c.execute(
            """
            SELECT Value, Name FROM 'ReportVariableWithTime' \
            WHERE Name IN (
                'Site Outdoor Air Drybulb Temperature',
                'Site Outdoor Air Wetbulb Temperature',
                'Site Outdoor Air Relative Humidity',
                'Zone Mean Air Temperature',
                'Zone Air Relative Humidity',
                'Zone Lights Electricity Energy',
                'Zone People Total Heating Energy',
                'Zone Electric Equipment Electricity Energy',
                'Zone Infiltration Standard Density Volume Flow Rate',
                'Zone Ventilation Standard Density Volume Flow Rate',
                'Zone Mechanical Ventilation Standard Density Volume Flow Rate'
            )
        """
        )
        results = c.fetchall()
        drybulb_temperatures = [value for value, name in results if name == "Site Outdoor Air Drybulb Temperature"]
        wetbulb_temperatures = [value for value, name in results if name == "Site Outdoor Air Wetbulb Temperature"]
        relative_humidities = [value for value, name in results if name == "Site Outdoor Air Relative Humidity"]
        zone_mean_air_temperatures = [value for value, name in results if name == "Zone Mean Air Temperature"]
        zone_air_relative_humidities = [value for value, name in results if name == "Zone Air Relative Humidity"]
        zone_lights_electricity_energy = [value for value, name in results if name == "Zone Lights Electricity Energy"]
        zone_people_total_heating_energy = [
            value for value, name in results if name == "Zone People Total Heating Energy"
        ]
        zone_electric_equipment_electricity_energy = [
            value for value, name in results if name == "Zone Electric Equipment Electricity Energy"
        ]
        zone_infiltration_standard_density_volume_flow_rate = [
            value for value, name in results if name == "Zone Infiltration Standard Density Volume Flow Rate"
        ]
        zone_ventilation_standard_density_volume_flow_rate = [
            value for value, name in results if name == "Zone Ventilation Standard Density Volume Flow Rate"
        ]
        zone_mechanical_ventilation_standard_density_volume_flow_rate = [
            value for value, name in results if name == "Zone Mechanical Ventilation Standard Density Volume Flow Rate"
        ]

        total_purchased_electricity_kwh_ = {
            "drybulb_temperatures": drybulb_temperatures,
            "wetbulb_temperatures": wetbulb_temperatures,
            "relative_humidities": relative_humidities,
            "zone_mean_air_temperatures": zone_mean_air_temperatures,
            "zone_air_relative_humidities": zone_air_relative_humidities,
            "zone_lights_electricity_energy": zone_lights_electricity_energy,
            "zone_people_total_heating_energy": zone_people_total_heating_energy,
            "zone_electric_equipment_electricity_energy": zone_electric_equipment_electricity_energy,
            "zone_infiltration_standard_density_volume_flow_rate": zone_infiltration_standard_density_volume_flow_rate,
            "zone_ventilation_standard_density_volume_flow_rate": zone_ventilation_standard_density_volume_flow_rate,
            "zone_mechanical_ventilation_standard_density_volume_flow_rate": zone_mechanical_ventilation_standard_density_volume_flow_rate,
        }
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return total_purchased_electricity_kwh_


def generate_graph(_phius_data: dict, _hbrv_data: dict, _title: str, _units: str, _filename: str):
    phius_plot_data = pd.DataFrame(_phius_data)
    phius_plot_data.index = pd.date_range(start="1/1/2020", periods=len(phius_plot_data), freq="h")
    phius_plot_data.index = phius_plot_data.index.strftime("%Y-%m-%d %H:%M:%S")

    hbrv_plot_data = pd.DataFrame(_hbrv_data)
    hbrv_plot_data.index = pd.date_range(start="1/1/2020", periods=len(hbrv_plot_data), freq="h")
    hbrv_plot_data.index = hbrv_plot_data.index.strftime("%Y-%m-%d %H:%M:%S")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=phius_plot_data.index, y=hbrv_plot_data[0], mode="lines", name="Phius-GUI", line=dict(width=0.5))
    )
    fig.add_trace(
        go.Scatter(
            x=hbrv_plot_data.index, y=hbrv_plot_data[0], mode="lines", name="Honeybee-REVIVE", line=dict(width=0.5)
        )
    )

    # Update layout
    fig.update_layout(
        title=_title,
        xaxis_title="Time",
        yaxis_title=_units,
        width=2000,  # Set plot width
        height=500,  # Set plot height
    )

    # Save the graph as a PNG file
    fig.write_image(Path(str(__file__)).parent / "energy_plus" / "png" / f"{_filename}.png")


if __name__ == "__main__":
    phius_gui_SQL = Path("tests/adorb/phius_gui/run/eplusout.sql")
    hbrv_SQL = Path("tests/adorb/hbrv/hb_revive_ADORB_model/openstudio/run/run/eplusout.sql")

    phius_data = get_from_sql(phius_gui_SQL)
    hbrv_data = get_from_sql(hbrv_SQL)

    generate_graph(
        phius_data["drybulb_temperatures"],
        hbrv_data["drybulb_temperatures"],
        "Outdoor Drybulb Temperature",
        "Temperature (°C)",
        "site_outdoor_air_drybulb_temperature",
    )
    generate_graph(
        phius_data["wetbulb_temperatures"],
        hbrv_data["wetbulb_temperatures"],
        "Outdoor Wetbulb Temperature",
        "Temperature (°C)",
        "site_outdoor_air_wetbulb_temperature",
    )
    generate_graph(
        phius_data["relative_humidities"],
        hbrv_data["relative_humidities"],
        "Outdoor Relative Humidity",
        "Relative Humidity (%)",
        "site_outdoor_air_relative_humidity",
    )
    generate_graph(
        phius_data["zone_mean_air_temperatures"],
        hbrv_data["zone_mean_air_temperatures"],
        "Zone Mean Air Temperature",
        "Temperature (°C)",
        "zone_mean_air_temperature",
    )
    generate_graph(
        phius_data["zone_air_relative_humidities"],
        hbrv_data["zone_air_relative_humidities"],
        "Zone Air Relative Humidity",
        "Relative Humidity (%)",
        "zone_air_relative_humidity",
    )
    generate_graph(
        phius_data["zone_lights_electricity_energy"],
        hbrv_data["zone_lights_electricity_energy"],
        "Zone Lights Electricity Energy",
        "Energy (J)",
        "zone_lights_electricity_energy",
    )
    generate_graph(
        phius_data["zone_people_total_heating_energy"],
        hbrv_data["zone_people_total_heating_energy"],
        "Zone People Total Heating Energy",
        "Energy (J)",
        "zone_people_total_heating_energy",
    )
    generate_graph(
        phius_data["zone_electric_equipment_electricity_energy"],
        hbrv_data["zone_electric_equipment_electricity_energy"],
        "Zone Electric Equipment Electricity Energy",
        "Energy (J)",
        "zone_electric_equipment_electricity_energy",
    )
    generate_graph(
        phius_data["zone_infiltration_standard_density_volume_flow_rate"],
        hbrv_data["zone_infiltration_standard_density_volume_flow_rate"],
        "Zone Infiltration Standard Density Volume Flow Rate",
        "Volume Flow Rate (m³/s)",
        "zone_infiltration_standard_density_volume_flow_rate",
    )
    generate_graph(
        phius_data["zone_ventilation_standard_density_volume_flow_rate"],
        hbrv_data["zone_ventilation_standard_density_volume_flow_rate"],
        "Zone Ventilation (Windows) Standard Density Volume Flow Rate",
        "Volume Flow Rate (m³/s)",
        "zone_ventilation_standard_density_volume_flow_rate",
    )
    generate_graph(
        phius_data["zone_mechanical_ventilation_standard_density_volume_flow_rate"],
        hbrv_data["zone_mechanical_ventilation_standard_density_volume_flow_rate"],
        "Zone Mechanical Ventilation Standard Density Volume Flow Rate",
        "Volume Flow Rate (m³/s)",
        "zone_mechanical_ventilation_standard_density_volume_flow_rate",
    )
