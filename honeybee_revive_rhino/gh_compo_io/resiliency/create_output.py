# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create Resiliency Output Files."""

import json
import os
import subprocess

try:
    from ladybug.datacollection import DailyCollection, HourlyContinuousCollection, MonthlyCollection
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


class GHCompo_CreateResiliencyOutputFiles(object):

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

        # -------------------------------------------------------------------------------
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

        # -------------------------------------------------------------------------------
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
