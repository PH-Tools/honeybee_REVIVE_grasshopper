# coding=utf-8
# -*- Python Version: 2.7 -*-

"""Module for reading in HBJSON and calculating ADORB Costs.

Running the 'calculate_HB_model_ADORB_cost' function will call a new subprocess using the 
Ladybug Tools Python 3.7 interpreter.
"""

from __future__ import division

import os
import subprocess

try:
    from typing import Any, Dict, List, Tuple, Union
except ImportError:
    pass  # Python 2.7

try:  # import the core honeybee dependencies
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


def _run_subprocess(commands):
    # type: (List[str]) -> Tuple[Any, Any]
    """Run a python subprocess.Popen, using the supplied commands

    Arguments:
    ----------
        * commands: (List[str]): A list of the commands to pass to Popen

    Returns:
    --------
        * Tuple:
            - [0]: stdout
            - [1]: stderr
    """
    # -- Create a new PYTHONHOME to avoid the Rhino-8 issues
    CUSTOM_ENV = os.environ.copy()
    CUSTOM_ENV["PYTHONHOME"] = ""

    use_shell = True if os.name == "nt" else False

    process = subprocess.Popen(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=use_shell,
        env=CUSTOM_ENV,
    )

    stdout, stderr = process.communicate()

    if stderr:
        if "Defaulting to Windows directory." in str(stderr):
            print("WARNING: {}".format(stderr))
        else:
            print(stderr)
            raise Exception(stderr)

    for _ in str(stdout).split("\\n"):
        print(_)

    return stdout, stderr


def _run_subprocess_from_shell(commands):
    # type: (List[str]) -> Tuple[Any, Any]
    """Run a python subprocess.Popen THROUGH a MacOS terminal via a shell, using the supplied commands.

    When talking to Excel on MacOS it is necessary to run through a Terminal since Rhino
    cannot get the right 'permissions' to interact with Excel. This is a workaround and not
    required on Windows OS.

    Arguments:
    ----------
        * _commands: (List[str]): A list of the commands to pass to Popen

    Returns:
    --------
        * Tuple:
            - [0]: stdout
            - [1]: stderr
    """

    # -- Create a new PYTHONHOME to avoid the Rhino-8 issues
    CUSTOM_ENV = os.environ.copy()
    CUSTOM_ENV["PYTHONHOME"] = ""

    use_shell = True if os.name == "nt" else False

    # -- Make sure the files are executable
    shell_file = commands[0]
    try:
        subprocess.check_call(["chmod", "u+x", shell_file])
    except Exception as e:
        print("Failed to make the shell file executable: {}".format(e))
        raise e

    python_script_path = commands[3]
    try:
        subprocess.check_call(["chmod", "u+x", python_script_path])
    except Exception as e:
        print("Failed to make the python script executable: {}".format(e))
        raise e

    process = subprocess.Popen(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=use_shell,
        env=CUSTOM_ENV,
    )

    stdout, stderr = process.communicate()

    if stderr:
        if "Defaulting to Windows directory." in str(stderr):
            print("Warning: {}".format(stderr))
        else:
            raise Exception(stderr)

    for _ in str(stdout).split("\\n"):
        print(_)

    return stdout, stderr


def calculate_HB_model_ADORB_cost(_hbjson_filepath, _results_file_name, _results_folder, *args, **kwargs):
    ## type: (str, str, str, bool, Union[bool, float], bool, int, List, Dict) -> tuple[str, str, str, str]
    """Read in an hbjson file and output a new WUFI XML file in the designated location.

    Arguments:
    ---------
        * _hbjson_filepath (str): File path to the HBJSON file to calculate ADORB for.
        * _save_file_name (str): The ADORB Results CSV filename.
        * _save_folder (str): The folder to save the new ADORB Results CSV file in.
        * args (List): Additional arguments to pass to the subprocess.
        * kwargs (Dict): Additional keyword arguments to pass to the subprocess.

    Returns:
    --------
        * tuple
            - [0] (str): The path to the output results CSV parent folder.
            - [1] (str): The output results CSV filename.
            - [2] (str): The stdout from the subprocess.
            - [3] (str): The stderr from the subprocess.
    """

    # -- Specify the path to the subprocess python script to run
    run_file_path = os.path.join(
        hb_folders.python_package_path, "ph_adorb", "from_HBJSON", "calc_hb_model_ADORB_costs.py"
    )

    # -- check the file paths
    assert os.path.isfile(_hbjson_filepath), "No HBJSON file found at {}.".format(_hbjson_filepath)
    assert os.path.isfile(run_file_path), "No Python file to run found at: {}".format(run_file_path)

    # -------------------------------------------------------------------------
    # -- Read in the HBJSON, convert to WUFI XML
    print("Using python interpreter: '{}'".format(hb_folders.python_exe_path))
    print("Running py script: '{}' Using HBJSON file: '{}'".format(run_file_path, _hbjson_filepath))
    commands = [
        hb_folders.python_exe_path,
        run_file_path,
    ]
    stdout, stderr = _run_subprocess(commands)

    # -------------------------------------------------------------------------
    # -- return the dir and filename of the xml created
    return _results_folder, _results_file_name, stdout, stderr
