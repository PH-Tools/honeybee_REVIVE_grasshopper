# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility: Call LBT Python3 to read the E+ SQL file and write the specified Output-Variable to a JSON file."""

import os

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_revive_rhino.gh_compo_io.run_subprocess import run_subprocess
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


def run(_py3_filepath, _sql_path, _output_variable_name, _json_filepath):
    # type: (str, str, str, str) -> tuple[bytes, bytes]
    """Using Ladybug's Python-3 interpreter: Get data from the E+ SQL file and write to a JSON file.

    ### Arguments:
        * _py3_filepath: The path to the Python-3 script to run.
        * _sql_path: The path to the EnergyPlus SQL file to use for the calculation.
        * _output_variable_name: The output variable name to get from the SQL file.
        * _json_filepath: The path to save the JSON file to.

    ### Returns:
        * tuple
            - [0] (bytes): The stdout from the subprocess.
            - [1] (bytes): The stderr from the subprocess.
    """

    # -- check the file paths
    assert os.path.isfile(_py3_filepath), "No Python file to run found at: {}".format(_py3_filepath)
    assert os.path.isfile(_sql_path), "No SQL file found at: {}".format(_sql_path)

    # -------------------------------------------------------------------------
    # -- Read in the HBJSON, convert to WUFI XML
    print("Using Python-3 interpreter: '{}'".format(hb_folders.python_exe_path))
    print("Running Python-3 script: '{}'".format(_py3_filepath))
    print("With the SQL file: '{}'".format(_sql_path))
    print("Getting the Variable: '{}'".format(_output_variable_name))
    print("Writing to: '{}'".format(_json_filepath))
    commands = [
        hb_folders.python_exe_path,  # -- The python3-interpreter to use
        _py3_filepath,  # --------------- The python3-script to run
        _sql_path,  # ------------------- The SQL file to use
        _json_filepath,  # -------------- The JSON file to save the data to
        _output_variable_name,  # ------- The output variable name to get
    ]
    stdout, stderr = run_subprocess(commands)

    # -------------------------------------------------------------------------
    return stdout, stderr
