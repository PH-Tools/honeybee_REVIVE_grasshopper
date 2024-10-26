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
    from ladybug.dt import DateTime
    from ladybug.header import Header
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

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
SummerHeatIndexHours = namedtuple("Output", ["caution", "warning", "danger", "extreme_danger"])


def hourly_collection(header, data):
    # type: (Header, list[Record]) -> HourlyContinuousCollection
    """Create an HourlyContinuousCollection from a header and some data."""

    return HourlyContinuousCollection(
        header,
        values=[r.value for r in sorted(data, key=lambda x: x.timestamp)],
    )


def build_summer_heat_index_HourlyCollection(
    _summer_zone_names_,
    _heat_index_caution,
    _heat_index_warning,
    _heat_index_danger,
    _heat_index_extreme_danger,
):
    # type: (list[str], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]]) -> SummerHeatIndexHours
    """Build the Heat-Index HourlyCollections for the summer months."""

    extreme_danger_hours_ = DataTree[HourlyContinuousCollection]()
    danger_hours_ = DataTree[HourlyContinuousCollection]()
    warning_hours_ = DataTree[HourlyContinuousCollection]()
    caution_hours_ = DataTree[HourlyContinuousCollection]()

    for i, zone_name in enumerate(_summer_zone_names_):
        times = [r.timestamp for r in sorted(_heat_index_extreme_danger[zone_name], key=lambda x: x.timestamp)]
        st, end = min(times), max(times)
        header = Header(
            data_type=Fraction(),
            unit="fraction",
            analysis_period=AnalysisPeriod(st.month, st.day, st.hour, end.month, end.day, end.hour),
            metadata={"zone": zone_name},
        )

        extreme_danger_hours_.Add(hourly_collection(header, _heat_index_extreme_danger[zone_name]), GH_Path(i))
        danger_hours_.Add(hourly_collection(header, _heat_index_danger[zone_name]), GH_Path(i))
        warning_hours_.Add(hourly_collection(header, _heat_index_warning[zone_name]), GH_Path(i))
        caution_hours_.Add(hourly_collection(header, _heat_index_caution[zone_name]), GH_Path(i))

    return SummerHeatIndexHours(caution_hours_, warning_hours_, danger_hours_, extreme_danger_hours_)


def calculate_heat_index_hours(_heat_index_hourly_records):
    # type: (list[dict]) -> tuple[dict[ZoneName, list[Record]], ...]
    """Calculate the Heat-Index hours for the summer months."""
    SUMMER_CAUTION_THRESHOLD = 26.7  # 80 deg-F
    SUMMER_WARNING_THRESHOLD = 32.2  # 90 deg-F
    SUMMER_DANGER_THRESHOLD = 39.4  # 103 deg-F
    SUMMER_EXTREME_DANGER_THRESHOLD = 51.7  # 125 deg-F

    heat_index_caution = defaultdict(list)
    heat_index_warning = defaultdict(list)
    heat_index_danger = defaultdict(list)
    heat_index_extreme_danger = defaultdict(list)
    for record in _heat_index_hourly_records:
        timestamp = datetime.utcfromtimestamp(record["Date"] / 1000.0)  # milliseconds to seconds
        lbt_timestamp = DateTime(timestamp.month, timestamp.day, timestamp.hour)

        if record["Value"] >= SUMMER_EXTREME_DANGER_THRESHOLD:
            heat_index_extreme_danger[record["Zone"]].append(Record(lbt_timestamp, 1))
        else:
            heat_index_extreme_danger[record["Zone"]].append(Record(lbt_timestamp, 0))

        if SUMMER_EXTREME_DANGER_THRESHOLD > record["Value"] >= SUMMER_DANGER_THRESHOLD:
            heat_index_danger[record["Zone"]].append(Record(lbt_timestamp, 1))
        else:
            heat_index_danger[record["Zone"]].append(Record(lbt_timestamp, 0))

        if SUMMER_DANGER_THRESHOLD > record["Value"] >= SUMMER_WARNING_THRESHOLD:
            heat_index_warning[record["Zone"]].append(Record(lbt_timestamp, 1))
        else:
            heat_index_warning[record["Zone"]].append(Record(lbt_timestamp, 0))

        if SUMMER_WARNING_THRESHOLD > record["Value"] >= SUMMER_CAUTION_THRESHOLD:
            heat_index_caution[record["Zone"]].append(Record(lbt_timestamp, 1))
        else:
            heat_index_caution[record["Zone"]].append(Record(lbt_timestamp, 0))

    return heat_index_caution, heat_index_warning, heat_index_danger, heat_index_extreme_danger


class GHCompo_ResiliencySummerOutput(object):

    def __init__(self, _IGH, _sql_path, _folder, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, list, dict) -> None
        self.IGH = _IGH
        self.sql_path = _sql_path
        self.results_folder_path = _folder or hb_folders.default_simulation_folder

    @property
    def json_filepath(self):
        # type: () -> str
        """Get the file path to save the generated JSON file to."""
        return os.path.join(self.results_folder_path, "{}.json".format("resilience_heat_index_data"))

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
        if not self.ready:
            return None, None, None, None, None

        # --------------------------------------------------------------------------------------------------------------
        # -- Call Python3 to Generate Graphs
        # -- This must be done using Python3 since we want to use Pandas and the Plotly library
        summer_graphs_py3_script_filepath = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_summer_graphs.py"
        )
        stdout, stderr, results_folder_path = _generate_graphs.run(
            _py3_filepath=summer_graphs_py3_script_filepath,
            _sql_path=self.sql_path,
            _results_folder_path=self.results_folder_path,
        )
        self.give_user_warnings(stdout, stderr)

        # --------------------------------------------------------------------------------------------------------------
        # -- Call Python3 to get the SQL data and write it out to a JSON file
        # -- This must be done using Python3 since Rhino's IronPython does not support the sqlite3 module on MacOS
        py3_script = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_hourly_data.py"
        )
        stdout, stderr = _sql_data_to_json.run(
            _py3_filepath=py3_script,
            _sql_path=self.sql_path,
            _output_variable_name="Zone Heat Index",
            _json_filepath=self.json_filepath,
        )
        self.give_user_warnings(stdout, stderr)

        # --------------------------------------------------------------------------------------------------------------
        # -- Calculate and organize the outputs for Summer Heat-Index Hours
        heat_index_hourly_records = self.read_json_file_data(self.json_filepath)
        heat_index_caution, heat_index_warning, heat_index_danger, heat_index_extreme_danger = (
            calculate_heat_index_hours(heat_index_hourly_records)
        )
        summer_zone_names_ = sorted(
            set(heat_index_caution.keys())
            | set(heat_index_warning.keys())
            | set(heat_index_danger.keys())
            | set(heat_index_extreme_danger.keys())
        )
        summer_heat_index_hourly_collections = build_summer_heat_index_HourlyCollection(
            summer_zone_names_,
            heat_index_caution,
            heat_index_warning,
            heat_index_danger,
            heat_index_extreme_danger,
        )

        # --------------------------------------------------------------------------------------------------------------
        return (
            summer_heat_index_hourly_collections.caution,
            summer_heat_index_hourly_collections.warning,
            summer_heat_index_hourly_collections.danger,
            summer_heat_index_hourly_collections.extreme_danger,
            results_folder_path,
        )
