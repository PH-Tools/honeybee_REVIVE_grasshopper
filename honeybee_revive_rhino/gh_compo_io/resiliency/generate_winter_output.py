# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create Resiliency Output Files."""

import json
import os
from collections import defaultdict, namedtuple
from datetime import datetime

try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        ZoneName = str
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import Grasshopper:\n\t{}".format(e))

try:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.fraction import Fraction
    from ladybug.datatype.temperaturedelta import TemperatureDelta
    from ladybug.dt import DateTime
    from ladybug.header import Header
except ImportError as e:
    raise ImportError("\nFailed to import Ladybug:\n\t{}".format(e))

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from honeybee_revive_rhino.gh_compo_io.resiliency import _generate_graphs, _sql_data_to_json
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_revive_rhino:\n\t{}".format(e))

Record = namedtuple("Record", ["timestamp", "value"])


def hourly_collection(header, data):
    # type: (Header, list[Record]) -> HourlyContinuousCollection
    """Create an HourlyContinuousCollection from a header and some data."""

    return HourlyContinuousCollection(
        header,
        values=[r.value for r in sorted(data, key=lambda x: x.timestamp)],
    )


def calculate_SET_degree_hours(_SET_hourly_records):
    # type: (list[dict]) -> tuple[dict[ZoneName, list[Record]], dict[ZoneName, list[Record]]]
    """Calculate the SET degree-hours below 12C and below 2C."""
    SET_DEG_C_THRESHOLD_1 = 12.22222  # 54 deg-F
    SET_DEG_C_THRESHOLD_2 = 2.22222  # 36 deg-F

    set_degree_hours_below_12C = defaultdict(list)
    set_degree_hours_below_2C = defaultdict(list)
    for record in _SET_hourly_records:
        timestamp = datetime.utcfromtimestamp(record["Date"] / 1000.0)  # milliseconds to seconds
        lbt_timestamp = DateTime(timestamp.month, timestamp.day, timestamp.hour)
        set_degree_hours_below_12C[record["Zone"]].append(
            Record(lbt_timestamp, max(SET_DEG_C_THRESHOLD_1 - record["Value"], 0))
        )
        set_degree_hours_below_2C[record["Zone"]].append(
            Record(lbt_timestamp, max(SET_DEG_C_THRESHOLD_2 - record["Value"], 0))
        )

    return set_degree_hours_below_12C, set_degree_hours_below_2C


def build_winter_SET_HourlyCollections(_winter_zone_names, _set_degree_hours_below_12C, _set_degree_hours_below_2C):
    # type: (list[ZoneName], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]]) -> tuple[DataTree[HourlyContinuousCollection], DataTree[HourlyContinuousCollection]]
    """Build the SET HourlyCollections for the winter months."""

    set_hours_below_12C_ = DataTree[HourlyContinuousCollection]()
    set_hours_below_2C_ = DataTree[HourlyContinuousCollection]()

    for i, zone_name in enumerate(_winter_zone_names):
        times = [r.timestamp for r in sorted(_set_degree_hours_below_12C[zone_name], key=lambda x: x.timestamp)]
        st, end = min(times), max(times)
        header = Header(
            data_type=TemperatureDelta(),
            unit="dC",
            analysis_period=AnalysisPeriod(st.month, st.day, st.hour, end.month, end.day, end.hour),
            metadata={"zone": zone_name},
        )
        set_hours_below_12C_.Add(hourly_collection(header, _set_degree_hours_below_12C[zone_name]), GH_Path(i))
        set_hours_below_2C_.Add(hourly_collection(header, _set_degree_hours_below_2C[zone_name]), GH_Path(i))

    return set_hours_below_12C_, set_hours_below_2C_


class GHCompo_ResiliencyWinterOutput(object):

    def __init__(self, _IGH, _sql_path, _folder, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, list, dict) -> None
        self.IGH = _IGH
        self.sql_path = _sql_path
        self.results_folder_path = _folder or hb_folders.default_simulation_folder

    @property
    def json_filepath(self):
        # type: () -> str
        """Get the file path to save the generated JSON file to."""
        return os.path.join(self.results_folder_path, "{}.json".format("resilience_SET_temperature"))

    def give_user_warnings(self, _stdout, _stderr):
        # type: (bytes, bytes | None) -> None
        """Give user warnings if any."""
        for line in str(_stdout).split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

        if _stderr:
            self.IGH.error(str(_stderr))

    def read_json_file_data(self, _json_filepath):
        # type: (str) -> list[dict]
        """Get the data from a JSON file."""
        with open(_json_filepath, "r") as json_file:
            return json.load(json_file)

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.sql_path or not os.path.exists(self.sql_path):
            return False
        else:
            return True

    def run(self):
        # type: () -> tuple
        if not self.ready:
            return None, None, None

        # --------------------------------------------------------------------------------------------------------------
        # -- Call Python3 to Generate Graphs
        # -- This must be done using Python3 since we want to use Pandas and the Plotly library
        summer_graphs_py3_script_filepath = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_winter_graphs.py"
        )
        stdout, stderr, results_folder_path = _generate_graphs.run(
            _py3_filepath=summer_graphs_py3_script_filepath,
            _sql_path=self.sql_path,
            _results_folder_path=self.results_folder_path,
        )
        self.give_user_warnings(stdout, stderr)

        # --------------------------------------------------------------------------------------------------------------
        # --- Get the SQL data and write it out to a JSON file
        py3_script = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_hourly_data.py"
        )
        stdout, stderr = _sql_data_to_json.run(
            _py3_filepath=py3_script,
            _sql_path=self.sql_path,
            _output_variable_name="Zone Thermal Comfort Pierce Model Standard Effective Temperature",
            _json_filepath=self.json_filepath,
        )
        self.give_user_warnings(stdout, stderr)

        # --------------------------------------------------------------------------------------------------------------
        # -- Calculate and organize the outputs for Winter SET Degree-Hours
        SET_hourly_records = self.read_json_file_data(self.json_filepath)
        set_degree_hours_below_12C, set_degree_hours_below_2C = calculate_SET_degree_hours(SET_hourly_records)
        winter_zone_names = sorted(set(set_degree_hours_below_12C.keys()) | set(set_degree_hours_below_2C.keys()))
        winter_set_hours_below_12C_, winter_set_hours_below_2C_ = build_winter_SET_HourlyCollections(
            winter_zone_names, set_degree_hours_below_12C, set_degree_hours_below_2C
        )

        return winter_set_hours_below_12C_, winter_set_hours_below_2C_, results_folder_path
