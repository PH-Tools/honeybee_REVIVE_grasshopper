# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create Resiliency Output Files."""

import os
import subprocess
import json

try:
    from ladybug.datacollection import HourlyContinuousCollection, MonthlyCollection, DailyCollection
    from ladybug.sql import SQLiteResult
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
    from honeybee_revive_rhino.gh_compo_io.run_subprocess import run_subprocess
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Python-3 ADORB Runner Functions


def run_graph_generator(_sql_path, _py3_filepath, _results_folder_path, *args, **kwargs):
    # type: (str, str, str, list, dict) -> tuple[bytes, bytes, str]
    """Using Ladybug's Python-3 interpreter: read in the SQL file and generate the Winter Resiliency HTML graphs.

    ### Arguments:
        * _sql_path: The path to the EnergyPlus SQL file to use for the calculation.
        * _py3_filepath: The path to the Python-3 script to run.
        * _results_folder_path: The folder to save the generated HTML file(s) to.
        * args: Additional arguments to pass to the subprocess. (ignored)
        * kwargs: Additional keyword arguments to pass to the subprocess. (ignored)

    ### Returns:
        * tuple
            - [0] (bytes): The stdout from the subprocess.
            - [1] (bytes): The stderr from the subprocess.
            - [2] (str): The path to the output folder with the HTML files.
    """

    # -- check the file paths
    assert os.path.isfile(_py3_filepath), "No Python file to run found at: {}".format(_py3_filepath)
    assert os.path.isfile(_sql_path), "No SQL file found at: {}".format(_sql_path)

    # -- Check the output location
    if not os.path.exists(_results_folder_path) or not os.path.isdir(_results_folder_path):
        os.makedirs(_results_folder_path)

    # -------------------------------------------------------------------------
    # -- Read in the HBJSON, convert to WUFI XML
    print("Using Python-3 interpreter: '{}'".format(hb_folders.python_exe_path))
    print("Running Python-3 script: '{}'".format(_py3_filepath))
    print("With the SQL file: '{}'".format(_sql_path))
    commands = [
        hb_folders.python_exe_path,  # -- The python3-interpreter to use
        _py3_filepath,  # --------- The python3-script to run
        _sql_path,  # ------------------- The SQL file to use
        _results_folder_path,  # -------- The HTML folder path to save the graphs to
    ]
    stdout, stderr = run_subprocess(commands)

    # -------------------------------------------------------------------------
    # -- return the dir and filename of the xml created
    return stdout, stderr, _results_folder_path


# -----------------------------------------------------------------------------
# -- .........


# class OutputData(object):
#     """A wrapper class to hold the output data from the SQL file."""

#     def __init__(self):
#         self.outdoor_air_dewpoint_temperature = None  # type: HourlyContinuousCollection | None
#         self.outdoor_air_drybulb_temperature = None  # type: HourlyContinuousCollection | None
#         self.outdoor_air_humidity_ratio = None  # type: HourlyContinuousCollection | None
#         self.outdoor_air_relative_humidity = None  # type: HourlyContinuousCollection | None
#         self.outdoor_air_wetbulb_temperature = None  # type: HourlyContinuousCollection | None
#         self.zone_air_relative_humidity = None  # type: HourlyContinuousCollection | None
#         self.zone_mean_air_temperature = None  # type: HourlyContinuousCollection | None
#         self.zone_mean_radiant_temperature = None  # type: HourlyContinuousCollection | None
#         self.zone_SET_temperature = None  # type: HourlyContinuousCollection | None


# def serialize_data(data_dicts):
#     # type: (list[dict]) -> list[HourlyContinuousCollection] | list[MonthlyCollection] | list[DailyCollection]
#     """Re-serialize a list of collection dictionaries."""

#     if len(data_dicts) == 0:
#         return []
#     elif data_dicts[0]["type"] == "HourlyContinuous":
#         return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
#     elif data_dicts[0]["type"] == "Monthly":
#         return [MonthlyCollection.from_dict(data) for data in data_dicts]
#     elif data_dicts[0]["type"] == "Daily":
#         return [DailyCollection.from_dict(data) for data in data_dicts]
#     else:
#         return []


# def get_sql_data(_sql, _output_names):
#     # type: (str, tuple[str, ...]) -> OutputData
#     """Get the data from the SQL file."""
#     output_data_ = OutputData()

#     if os.name == "nt":
#         # we are on windows; use IronPython like usual
#         sql_obj = SQLiteResult(_sql)  # create the SQL result parsing object

#         # -- Package up the output data
#         output_data_.outdoor_air_dewpoint_temperature = sql_obj.data_collections_by_output_name(_output_names[0])
#         output_data_.outdoor_air_drybulb_temperature = sql_obj.data_collections_by_output_name(_output_names[1])
#         output_data_.outdoor_air_humidity_ratio = sql_obj.data_collections_by_output_name(_output_names[2])
#         output_data_.outdoor_air_relative_humidity = sql_obj.data_collections_by_output_name(_output_names[3])
#         output_data_.outdoor_air_wetbulb_temperature = sql_obj.data_collections_by_output_name(_output_names[4])
#         output_data_.zone_air_relative_humidity = sql_obj.data_collections_by_output_name(_output_names[5])
#         output_data_.zone_mean_air_temperature = sql_obj.data_collections_by_output_name(_output_names[6])
#         output_data_.zone_mean_radiant_temperature = sql_obj.data_collections_by_output_name(_output_names[7])
#         output_data_.zone_SET_temperature = sql_obj.data_collections_by_output_name(_output_names[8])
#     else:
#         # we are on Mac; sqlite3 module doesn't work in Mac IronPython
#         # Execute the honeybee CLI to obtain the results via CPython

#         # -- Build the command
#         cmds = [hb_folders.python_exe_path, "-m", "honeybee_energy", "result", "data-by-outputs", _sql]
#         for output_name in _output_names:
#             out_str = json.dumps(output_name) if isinstance(output_name, tuple) else '["{}"]'.format(output_name)
#             cmds.append(out_str)

#         # -- Run the command. Remember we need to do this PYTHONHOME thing in Rhino 8 now.
#         custom_env = os.environ.copy()
#         custom_env["PYTHONHOME"] = ""
#         process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
#         stdout = process.communicate()
#         data_dicts = json.loads(stdout[0])

#         # -- Package up the output data
#         # TODO: Handle index errors...
#         output_data_.outdoor_air_dewpoint_temperature = data_dicts[0]
#         output_data_.outdoor_air_drybulb_temperature = data_dicts[1]
#         output_data_.outdoor_air_humidity_ratio = data_dicts[2]
#         output_data_.outdoor_air_relative_humidity = data_dicts[3]
#         output_data_.outdoor_air_wetbulb_temperature = data_dicts[4]
#         output_data_.zone_air_relative_humidity = data_dicts[5]
#         output_data_.zone_mean_air_temperature = data_dicts[6]
#         output_data_.zone_mean_radiant_temperature = data_dicts[7]
#         output_data_.zone_SET_temperature = data_dicts[8]

#     return output_data_


# -----------------------------------------------------------------------------
# -- Grasshopper Interface


class GHCompo_CreateResiliencyOutputFiles(object):

    OUTPUT_NAMES = (
        "Site Outdoor Air Dewpoint Temperature",
        "Site Outdoor Air Drybulb Temperature",
        "Site Outdoor Air Humidity Ratio",
        "Site Outdoor Air Relative Humidity",
        "Site Outdoor Air Wetbulb Temperature",
        "Zone Air Relative Humidity",
        "Zone Mean Air Temperature",
        "Zone Mean Radiant Temperature",
        "Zone Thermal Comfort Pierce Model Standard Effective Temperature",
    )

    def __init__(self, _IGH, _sql_path, _folder, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, list, dict) -> None
        self.IGH = _IGH
        self.sql_path = _sql_path
        self.results_folder_path = _folder or hb_folders.default_simulation_folder

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.sql_path or not os.path.exists(self.sql_path):
            return False
        else:
            return True

    def give_no_sql_data_warning(self):
        # type: () -> None
        """Give a warning if no data is found in the SQL file."""
        msg = (
            "No data found in the SQL file. Ensure that you set the correct Phius REVIVE Resiliency "
            "outputs by using the 'Set Resiliency Simulation Output Names' Grasshopper Component."
        )
        print(msg)
        self.IGH.warning(msg)

    def give_user_warnings(self, _stdout):
        # type: (bytes) -> None
        """Give user warnings if any."""
        for line in str(_stdout).split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

    def run(self):
        # type: () -> str | None
        if not self.ready:
            return None

        # -- Winter Graphs
        winter_graphs_py3_script_filepath = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_winter_graphs.py"
        )
        stdout, stderr, results_folder_path = run_graph_generator(
            _sql_path=self.sql_path,
            _py3_filepath=winter_graphs_py3_script_filepath,
            _results_folder_path=self.results_folder_path,
        )
        self.give_user_warnings(stdout)
        if stderr:
            print(stderr)

        # -- Summer Graphs
        summer_graphs_py3_script_filepath = os.path.join(
            hb_folders.python_package_path, "honeybee_revive", "output", "resilience_summer_graphs.py"
        )
        stdout, stderr, results_folder_path = run_graph_generator(
            _sql_path=self.sql_path,
            _py3_filepath=summer_graphs_py3_script_filepath,
            _results_folder_path=self.results_folder_path,
        )
        self.give_user_warnings(stdout)
        if stderr:
            print(stderr)

        return results_folder_path
