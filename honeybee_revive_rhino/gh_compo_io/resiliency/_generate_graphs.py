# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility: Call LBT Python3 to read the E+ SQL file and generate the resiliency graphs."""

import os

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_revive_rhino.gh_compo_io.run_subprocess import run_subprocess
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


def run(_py3_filepath, _sql_path, _results_folder_path):
    # type: (str, str, str) -> tuple[bytes, bytes, str]
    """Using Ladybug's Python-3 interpreter: read in the SQL file and generate the Winter Resiliency HTML graphs.

    ### Arguments:
        * _py3_filepath: The path to the Python-3 script to run.
        * _sql_path: The path to the EnergyPlus SQL file to use for the calculation.
        * _results_folder_path: The folder to save the generated HTML file(s) to.

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
    print("Outputting to : '{}'".format(_results_folder_path))
    commands = [
        hb_folders.python_exe_path,  # -- The python3-interpreter to use
        _py3_filepath,  # --------------- The python3-script to run
        _sql_path,  # ------------------- The SQL file to use
        _results_folder_path,  # -------- The HTML folder path to save the graphs to
    ]
    stdout, stderr = run_subprocess(commands)

    # -------------------------------------------------------------------------
    # -- return the dir and filename of the xml created
    return stdout, stderr, _results_folder_path
