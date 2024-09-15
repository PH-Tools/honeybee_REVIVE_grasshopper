# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Calculate ADORB Cost."""

import json
import os
import subprocess
import sys
from contextlib import contextmanager

try:
    from typing import Any, Generator, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders as hb_folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")


# -----------------------------------------------------------------------------
# -- Python-3 ADORB Runner Functions


def _run_subprocess(commands):
    # type: (list[str]) -> tuple[Any, Any]
    """Run a python subprocess.Popen, using the supplied commands

    Arguments:
    ----------
        * commands: (list[str]): A list of the commands to pass to Popen

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


def run_ADORB_calculator(_hbjson_filepath, _results_file_name, _results_folder, *args, **kwargs):
    ## type: (str, str, str, bool, Union[bool, float], bool, int, list, dict) -> tuple[str, str, str, str]
    """Using Ladybug's Python-3 interpreter: read in aa HBJSON model file and calculate the ADORB costs.

    Arguments:
    ---------
        * _hbjson_filepath (str): File path to the HBJSON model file to calculate ADORB for.
        * _save_file_name (str): The ADORB Results CSV filename.
        * _save_folder (str): The folder to save the new ADORB Results CSV file in.
        * args (list): Additional arguments to pass to the subprocess.
        * kwargs (dict): Additional keyword arguments to pass to the subprocess.

    Returns:
    --------
        * tuple
            - [0] (str): The path to the output results CSV parent folder.
            - [1] (str): The output results CSV filename.
            - [2] (str): The stdout from the subprocess.
            - [3] (str): The stderr from the subprocess.
    """

    # -- Specify the path to the actual subprocess python-3 script to run
    py3_script_filepath = os.path.join(
        hb_folders.python_package_path, "ph_adorb", "from_HBJSON", "calc_hb_model_ADORB_costs.py"
    )

    # -- check the file paths
    assert os.path.isfile(_hbjson_filepath), "No HBJSON file found at {}.".format(_hbjson_filepath)
    assert os.path.isfile(py3_script_filepath), "No Python file to run found at: {}".format(py3_script_filepath)

    # -------------------------------------------------------------------------
    # -- Read in the HBJSON, convert to WUFI XML
    print("Using Python-3 interpreter: '{}'".format(hb_folders.python_exe_path))
    print("Running Python-3 script: '{}' with the HBJSON file: '{}'".format(py3_script_filepath, _hbjson_filepath))
    commands = [
        hb_folders.python_exe_path,  # The interpreter to use
        py3_script_filepath,  # The script to run
        _hbjson_filepath,  # The HBJSON file to read in
        _results_file_name,  # The filename to save the results to
    ]
    stdout, stderr = _run_subprocess(commands)

    # -------------------------------------------------------------------------
    # -- return the dir and filename of the xml created
    return _results_folder, _results_file_name, stdout, stderr


# -----------------------------------------------------------------------------
# -- Utility Functions to create HBJSON file from Model


def _using_python_2():
    # type: () -> bool
    """Utility function: Returns True if the current Python interpreter is Python 2."""
    return sys.version_info < (3, 0)


def write_hb_model_to_json_file(_hb_model):
    # type: (Model) -> str
    """Write out a HB Model to a JSON file.

    Adapted from the Grasshopper "Honeybee - HB Dump Objects" Component
    """
    # -- Setup the file path
    file_name = "{}.hbjson".format(_hb_model.display_name)
    folder = hb_folders.default_simulation_folder
    hb_json_file_path = os.path.join(folder, file_name)

    try:
        if not os.path.isdir(folder):
            os.makedirs(folder)
    except Exception as e:
        raise Exception("Failed to create the folder for the model json file at: '{}'\n\t{}".format(folder, e))

    try:
        if os.path.isfile(hb_json_file_path):
            os.remove(hb_json_file_path)
    except Exception as e:
        raise Exception("Failed to remove an existing json file at:'{}'\n\t{}".format(hb_json_file_path, e))

    # -- Create the dictionary to be written to a JSON file
    obj_dict = _hb_model.to_dict()

    # -- Write the Model dictionary to a JSON file
    print("Writing HB-Model out to JSON file: {}".format(hb_json_file_path))
    if _using_python_2():
        # -- We need to manually encode it as UTF-8
        with open(hb_json_file_path, "wb") as fp:
            obj_str = json.dumps(obj_dict, ensure_ascii=False)
            fp.write(obj_str.encode("utf-8"))
    else:
        with open(hb_json_file_path, "w", encoding="utf-8") as fp:
            obj_str = json.dump(obj_dict, fp, ensure_ascii=False)

    return hb_json_file_path


@contextmanager
def model_as_json_file(_hb_model):
    # type: (Model) -> Generator[str, None, None]
    """Create a temporary JSON file for a HB Model. Remove it at the end of use.

    Usage:
    -------
    >>> with model_as_json_file(honeybee_model_object) as hb_json_filepath:
    >>>    # do something with the file
    """
    try:
        hb_json_file = write_hb_model_to_json_file(_hb_model)
        yield hb_json_file
    finally:
        if os.path.isfile(hb_json_file):
            print("Removing temporary JSON file: {}".format(hb_json_file))
            os.remove(hb_json_file)


# -----------------------------------------------------------------------------
# -- Grasshopper Interface


class GHCompo_CalculateADORBCost(object):
    """GHCompo Interface: HBPH - Write WUFI XML."""

    def __init__(self, _IGH, _hb_model, _calculate_ADORB, *args, **kwargs):
        # type: (gh_io.IGH, Model, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.hb_model = _hb_model
        self.calculate_ADORB = _calculate_ADORB

    def give_user_warnings(self, _stdout):
        # type: (str) -> None
        """Give user warnings if any."""

        for line in _stdout.split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

    def run(self):
        # type: () -> tuple[Optional[str], Optional[str]]
        print("running ADORB cost calculation")
        if not self.calculate_ADORB or not self.hb_model:
            return ("", "")

        with model_as_json_file(self.hb_model) as hb_json_filepath:
            saved_file_dir, saved_file_name, stdout, stderr = run_ADORB_calculator(
                _hbjson_filepath=hb_json_filepath,
                _results_file_name=os.path.join(os.path.dirname(__file__), "ADORB.csv"),
                _results_folder=hb_folders.default_simulation_folder,
            )
            self.give_user_warnings(stdout)
            print("ADORB costs output to: {}  |  {}".format(saved_file_dir, saved_file_name))

        return stdout, stderr
