# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Calc Resiliency Hours."""

from collections import defaultdict, namedtuple
import os
import json
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
    from ladybug.dt import DateTime
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.header import Header
    from ladybug.datatype.temperaturedelta import TemperatureDelta
    from ladybug.datatype.fraction import Fraction
    from ladybug.analysisperiod import AnalysisPeriod
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
    from honeybee_revive_rhino.gh_compo_io.run_subprocess import run_subprocess
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))

Record = namedtuple("Record", ["timestamp", "value"])


class GHCompo_CalcResiliencyHours(object):

    SET_JSON_FILE_NAME = "resilience_SET_data"
    HEAT_INDEX_JSON_FILE_NAME = "resilience_heat_index_data"
    SET_DEG_C_THRESHOLD_1 = 12.22222  # 54 deg-F
    SET_DEG_C_THRESHOLD_2 = 2.22222  # 36 deg-F
    SUMMER_CAUTION_THRESHOLD = 26.7  # 80 deg-F
    SUMMER_WARNING_THRESHOLD = 32.2  # 90 deg-F
    SUMMER_DANGER_THRESHOLD = 39.4  # 103 deg-F
    SUMMER_EXTREME_DANGER_THRESHOLD = 51.7  # 125 deg-F

    def __init__(self, _IGH, _sql_path, _folder, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, list, dict) -> None
        self.IGH = _IGH
        self.sql_path = _sql_path
        self.folder = _folder or hb_folders.default_simulation_folder

    def give_user_warnings(self, _stdout, _stderr):
        # type: (bytes, bytes | None) -> None
        """Give user warnings if any."""
        for line in str(_stdout).split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

        if _stderr:
            self.IGH.error(str(_stderr))

    def get_sql_data(self, _py3_filepath, *args, **kwargs):
        # type: (str, list, dict) -> tuple[bytes, bytes]
        """Using Ladybug's Python-3 interpreter: read in the SQL file and generate the Winter Resiliency HTML graphs.

        ### Arguments:
            * _py3_filepath: The path to the Python-3 script to run.
            * args: Additional arguments to pass to the subprocess. (ignored)
            * kwargs: Additional keyword arguments to pass to the subprocess. (ignored)

        ### Returns:
            * tuple
                - [0] (bytes): The stdout from the subprocess.
                - [1] (bytes): The stderr from the subprocess.
        """

        # -- check the file paths
        assert os.path.isfile(_py3_filepath), "No Python file to run found at: {}".format(_py3_filepath)
        assert os.path.isfile(self.sql_path), "No SQL file found at: {}".format(self.sql_path)

        # -------------------------------------------------------------------------
        # -- Read in the HBJSON, convert to WUFI XML
        print("Using Python-3 interpreter: '{}'".format(hb_folders.python_exe_path))
        print("Running Python-3 script: '{}'".format(_py3_filepath))
        print("With the SQL file: '{}'".format(self.sql_path))
        commands = [
            hb_folders.python_exe_path,  # -- The python3-interpreter to use
            _py3_filepath,  # --------------- The python3-script to run
            self.sql_path,  # --------------- The SQL file to use
            self.set_json_filepath,  # ------ The JSON file to save the data to
            self.heat_index_filepath,  # ---- The JSON file to save the data to
        ]
        stdout, stderr = run_subprocess(commands)

        # -------------------------------------------------------------------------
        return stdout, stderr

    @property
    def set_json_filepath(self):
        # type: () -> str
        """Get the file path to save the generated JSON file to."""
        return os.path.join(self.folder, "{}.json".format(self.SET_JSON_FILE_NAME))

    @property
    def heat_index_filepath(self):
        # type: () -> str
        """Get the file path to save the generated JSON file to."""
        return os.path.join(self.folder, "{}.json".format(self.HEAT_INDEX_JSON_FILE_NAME))

    def hourly_collection(self, header, data):
        # type: (Header, list[Record]) -> HourlyContinuousCollection
        """Create an HourlyContinuousCollection from the header and data."""

        return HourlyContinuousCollection(
            header,
            values=[r.value for r in sorted(data, key=lambda x: x.timestamp)],
        )

    def read_json_file_data(self, _json_filepath):
        # type: (str) -> list[dict]
        """Get the data from a JSON file."""
        with open(_json_filepath, "r") as json_file:
            return json.load(json_file)

    def calculate_SET_degree_hours(self, _SET_hourly_records):
        # type: (list[dict]) -> tuple[dict[ZoneName, list[Record]], dict[ZoneName, list[Record]]]
        """Calculate the SET degree-hours below 12C and below 2C."""

        set_degree_hours_below_12C = defaultdict(list)
        set_degree_hours_below_2C = defaultdict(list)
        for record in _SET_hourly_records:
            timestamp = datetime.utcfromtimestamp(record["Date"] / 1000.0)  # milliseconds to seconds
            lbt_timestamp = DateTime(timestamp.month, timestamp.day, timestamp.hour)
            set_degree_hours_below_12C[record["Zone"]].append(
                Record(lbt_timestamp, max(self.SET_DEG_C_THRESHOLD_1 - record["Value"], 0))
            )
            set_degree_hours_below_2C[record["Zone"]].append(
                Record(lbt_timestamp, max(self.SET_DEG_C_THRESHOLD_2 - record["Value"], 0))
            )

        return set_degree_hours_below_12C, set_degree_hours_below_2C

    def build_winter_SET_HourlyCollections(
        self, _winter_zone_names, _set_degree_hours_below_12C, _set_degree_hours_below_2C
    ):
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
            set_hours_below_12C_.Add(self.hourly_collection(header, _set_degree_hours_below_12C[zone_name]), GH_Path(i))
            set_hours_below_2C_.Add(self.hourly_collection(header, _set_degree_hours_below_2C[zone_name]), GH_Path(i))

        return set_hours_below_12C_, set_hours_below_2C_

    def calculate_heat_index_hours(self, _heat_index_hourly_records):
        # type: (list[dict]) -> tuple[dict[ZoneName, list[Record]], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]]]
        """Calculate the Heat-Index hours for the summer months."""

        heat_index_caution = defaultdict(list)
        heat_index_warning = defaultdict(list)
        heat_index_danger = defaultdict(list)
        heat_index_extreme_danger = defaultdict(list)
        for record in _heat_index_hourly_records:
            timestamp = datetime.utcfromtimestamp(record["Date"] / 1000.0)  # milliseconds to seconds
            lbt_timestamp = DateTime(timestamp.month, timestamp.day, timestamp.hour)

            if record["Value"] >= self.SUMMER_EXTREME_DANGER_THRESHOLD:
                heat_index_extreme_danger[record["Zone"]].append(Record(lbt_timestamp, 1))
            else:
                heat_index_extreme_danger[record["Zone"]].append(Record(lbt_timestamp, 0))

            if self.SUMMER_EXTREME_DANGER_THRESHOLD > record["Value"] >= self.SUMMER_DANGER_THRESHOLD:
                heat_index_danger[record["Zone"]].append(Record(lbt_timestamp, 1))
            else:
                heat_index_danger[record["Zone"]].append(Record(lbt_timestamp, 0))

            if self.SUMMER_DANGER_THRESHOLD > record["Value"] >= self.SUMMER_WARNING_THRESHOLD:
                heat_index_warning[record["Zone"]].append(Record(lbt_timestamp, 1))
            else:
                heat_index_warning[record["Zone"]].append(Record(lbt_timestamp, 0))

            if self.SUMMER_WARNING_THRESHOLD > record["Value"] >= self.SUMMER_CAUTION_THRESHOLD:
                heat_index_caution[record["Zone"]].append(Record(lbt_timestamp, 1))
            else:
                heat_index_caution[record["Zone"]].append(Record(lbt_timestamp, 0))

        return heat_index_caution, heat_index_warning, heat_index_danger, heat_index_extreme_danger

    def build_summer_heat_index_HourlyCollection(
        self,
        _summer_zone_names_,
        _heat_index_caution,
        _heat_index_warning,
        _heat_index_danger,
        _heat_index_extreme_danger,
    ):
        # type: (list[str], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]], dict[ZoneName, list[Record]]) -> Output
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

            extreme_danger_hours_.Add(self.hourly_collection(header, _heat_index_extreme_danger[zone_name]), GH_Path(i))
            danger_hours_.Add(self.hourly_collection(header, _heat_index_danger[zone_name]), GH_Path(i))
            warning_hours_.Add(self.hourly_collection(header, _heat_index_warning[zone_name]), GH_Path(i))
            caution_hours_.Add(self.hourly_collection(header, _heat_index_caution[zone_name]), GH_Path(i))

        Output = namedtuple("Output", ["caution", "warning", "danger", "extreme_danger"])
        return Output(caution_hours_, warning_hours_, danger_hours_, extreme_danger_hours_)

    @property
    def ready(self):
        # type: () -> bool
        """Check if the component is ready to run."""

        if not self.sql_path:
            return False
        return True

    def run(self):
        # type: () -> tuple[DataTree[HourlyContinuousCollection] | None, ...]
        """
        This will use subprocess to run the Python-3 script to get the data from the SQL file and then
        write it out to a JSON file. It will then read back in the JSON file and output the data as LBT HourlyContinuousCollection for Rhino/GH.
        This must be done using subprocess and Python-3 because sqlite3 does not work with Rhino/IronPython on MacOS.
        """

        if not self.ready:
            return None, None, None, None, None, None

        # --------------------------------------------------------------------------------------------------------------
        # --- Get the SQL data and write it out to a JSON file
        py3_script = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_hourly_data.py"
        )
        stdout, stderr = self.get_sql_data(py3_script)
        self.give_user_warnings(stdout, stderr)

        # --------------------------------------------------------------------------------------------------------------
        # -- Calculate and organize the outputs for Winter SET Degree-Hours
        SET_hourly_records = self.read_json_file_data(self.set_json_filepath)
        set_degree_hours_below_12C, set_degree_hours_below_2C = self.calculate_SET_degree_hours(SET_hourly_records)
        winter_zone_names = sorted(set(set_degree_hours_below_12C.keys()) | set(set_degree_hours_below_2C.keys()))
        winter_set_hours_below_12C_, winter_set_hours_below_2C_ = self.build_winter_SET_HourlyCollections(
            winter_zone_names, set_degree_hours_below_12C, set_degree_hours_below_2C
        )

        # --------------------------------------------------------------------------------------------------------------
        # -- Calculate and organize the outputs for Summer Heat-Index Hours
        heat_index_hourly_records = self.read_json_file_data(self.heat_index_filepath)
        heat_index_caution, heat_index_warning, heat_index_danger, heat_index_extreme_danger = (
            self.calculate_heat_index_hours(heat_index_hourly_records)
        )
        summer_zone_names_ = sorted(
            set(heat_index_caution.keys())
            | set(heat_index_warning.keys())
            | set(heat_index_danger.keys())
            | set(heat_index_extreme_danger.keys())
        )
        summer_heat_index_hourly_collections = self.build_summer_heat_index_HourlyCollection(
            summer_zone_names_,
            heat_index_caution,
            heat_index_warning,
            heat_index_danger,
            heat_index_extreme_danger,
        )

        # -- Output the data as a CSV file.

        return (
            winter_set_hours_below_12C_,
            winter_set_hours_below_2C_,
            summer_heat_index_hourly_collections.caution,
            summer_heat_index_hourly_collections.warning,
            summer_heat_index_hourly_collections.danger,
            summer_heat_index_hourly_collections.extreme_danger,
        )
