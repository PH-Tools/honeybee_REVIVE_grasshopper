from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

COLUMN_NAMES = {
    "energy_purchase_cost": {"hbrv": "pv_direct_energy", "phius": "pv_dirEn"},
    "energy_CO2_cost": {"hbrv": "pv_operational_CO2", "phius": "pv_opCO2"},
    "construction_purchase_cost": {"hbrv": "pv_direct_MR", "phius": "pv_dirMR"},
    "construction_CO2_cost": {"hbrv": "pv_embodied_CO2", "phius": "pv_emCO2"},
    "grid_transition_cost": {"hbrv": "pv_e_trans", "phius": "pv_eTrans"},
}


def generate_plot(_phius_gui_ADORB: pd.DataFrame, _hbrv_ADORB: pd.DataFrame, _type: str, _title: str) -> None:
    phius_direct_energy = _phius_gui_ADORB[COLUMN_NAMES[_type]["phius"]]
    hbrv_direct_energy = _hbrv_ADORB[COLUMN_NAMES[_type]["hbrv"]]

    # Create the line graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=phius_gui_ADORB.index, y=phius_direct_energy, mode="lines", name="PHIUS-GUI"))
    fig.add_trace(go.Scatter(x=hbrv_ADORB.index, y=hbrv_direct_energy, mode="lines", name="Honeybee-REVIVE"))

    # Determine y-axis lower bound
    y_min = min(phius_direct_energy[0].min(), hbrv_direct_energy[0].min())
    yaxis_range = [0, None] if y_min >= 0 else [None, None]

    # Update layout
    fig.update_layout(
        title=_title,
        xaxis_title="Years from Start",
        yaxis_title="PV-Cost",
        yaxis=dict(range=yaxis_range),
    )

    # Save the graph as a PNG file
    fig.write_image(Path(str(__file__)).parent / "adorb_cost" / "png" / f"{_type}.png")

    # Save the graph as an HTML file
    with open(Path(str(__file__)).parent / "adorb_cost" / "html" / f"{_type}.html", "w") as f:
        f.write(fig.to_html(fig, full_html=False, include_plotlyjs="cdn"))


if __name__ == "__main__":
    phius_gui_ADORB = pd.read_csv(
        Path("tests/adorb/phius_gui/results/M_10W-20S_StateCollegePA_BASE_NV_ADORBresults.csv")
    )
    hbrv_ADORB = pd.read_csv(Path("tests/adorb/hbrv/hb_revive_ADORB_results/hb_revive_ADORB_model_yearly.csv"))

    generate_plot(
        phius_gui_ADORB, hbrv_ADORB, "energy_purchase_cost", "Present-Value ($USD) of Yearly Energy Purchase Cost"
    )
    generate_plot(phius_gui_ADORB, hbrv_ADORB, "energy_CO2_cost", "Present-Value ($USD) of Yearly Energy CO2 Cost")
    generate_plot(
        phius_gui_ADORB,
        hbrv_ADORB,
        "construction_purchase_cost",
        "Present-Value ($USD) of Yearly Construction Purchase Cost",
    )
    generate_plot(
        phius_gui_ADORB, hbrv_ADORB, "construction_CO2_cost", "Present-Value ($USD) of Yearly Construction CO2 Cost"
    )
    generate_plot(
        phius_gui_ADORB, hbrv_ADORB, "grid_transition_cost", "Present-Value ($USD) of Yearly Grid-Transition Cost"
    )
