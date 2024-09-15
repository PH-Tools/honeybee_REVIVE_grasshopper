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
    # type: (list[str]) -> tuple[bytes, bytes]
    """Run a python subprocess.Popen, using the supplied commands

    ### Arguments:
        * commands: A list of the commands to pass to Popen
    ### Returns:
        * tuple:
            * [0] (bytes): stdout
            * [1] (bytes): stderr
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


def run_ADORB_calculator(_hbjson_filepath, _results_file_path, *args, **kwargs):
    # type: (str, str, list, dict) -> tuple[str, bytes, bytes]
    """Using Ladybug's Python-3 interpreter: read in aa HBJSON model file and calculate the ADORB costs.

    ### Arguments:
        * _hbjson_filepath: File path to the HBJSON model file to calculate ADORB for.
        * _results_file_path: The ADORB Results CSV file path.
        * args: Additional arguments to pass to the subprocess.
        * kwargs: Additional keyword arguments to pass to the subprocess.

    ### Returns:
        * tuple
            - [0] (str): The path to the output results CSV parent folder.
            - [1] (str): The output results CSV filename.
            - [2] (bytes): The stdout from the subprocess.
            - [3] (bytes): The stderr from the subprocess.
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
    print("Running Python-3 script: '{}'".format(py3_script_filepath))
    print("Using the HBJSON file: '{}'".format(_hbjson_filepath))
    commands = [
        hb_folders.python_exe_path,  # -- The interpreter to use
        py3_script_filepath,  # --------- The script to run
        _hbjson_filepath,  # ------------ The HBJSON file to read in
        _results_file_path,  # ---------- The CSV file path to save the results to
    ]
    stdout, stderr = _run_subprocess(commands)

    # -------------------------------------------------------------------------
    # -- return the dir and filename of the xml created
    return _results_file_path, stdout, stderr


# -----------------------------------------------------------------------------
# -- Utility Functions to create HBJSON file from Model


def _using_python_2():
    # type: () -> bool
    """Utility function: Returns True if the current Python interpreter is Python 2."""
    return sys.version_info < (3, 0)


def write_hb_model_to_json_file(_hb_model, _hbjson_output_file_path):
    # type: (Model, str) -> str
    """Write out a HB Model to a JSON file.

    Adapted from the Grasshopper "Honeybee - HB Dump Objects" Component

    ### Arguments:
        * _hb_model: The Honeybee Model to write to a JSON file.
        * _hbjson_output_file_path: The full file path to write the JSON file to.
    ### Returns:
        * str: The full file path to the JSON file written.
    """
    # -- Remove the HBJSON file if it already exists
    try:
        if os.path.isfile(_hbjson_output_file_path):
            os.remove(_hbjson_output_file_path)
    except Exception as e:
        raise Exception("Failed to remove an existing json file at:'{}'\n\t{}".format(_hbjson_output_file_path, e))

    # -- Create the dictionary to be written to a JSON file
    obj_dict = _hb_model.to_dict()

    # -- Write the Model dictionary to a JSON file
    print("Writing HB-Model out to JSON file: {}".format(_hbjson_output_file_path))
    if _using_python_2():
        # -- We need to manually encode it as UTF-8
        with open(_hbjson_output_file_path, "wb") as fp:
            obj_str = json.dumps(obj_dict, ensure_ascii=False)
            fp.write(obj_str.encode("utf-8"))
    else:
        with open(_hbjson_output_file_path, "w", encoding="utf-8") as fp:
            obj_str = json.dump(obj_dict, fp, ensure_ascii=False)

    return _hbjson_output_file_path


@contextmanager
def model_as_json_file(_hb_model, _hbjson_output_file_path):
    # type: (Model, str) -> Generator[str, None, None]
    """Create a temporary JSON file for a HB Model. Removes the file at the end of use.

    ### Usage:
    >>> with model_as_json_file(honeybee_model_object) as hb_json_filepath:
    >>>    # do something with the file

    ### Arguments:
        * _hb_model: The Honeybee Model to write to a JSON file.
        * _hbjson_output_file_path: The full file path to write the JSON file to.
    ### Yields:
        * str: The full file path to the JSON file written.
    """

    try:
        hb_json_file = write_hb_model_to_json_file(_hb_model, _hbjson_output_file_path)
        yield hb_json_file
    finally:
        if os.path.isfile(hb_json_file):
            print("Removing temporary JSON file: {}".format(hb_json_file))
            os.remove(hb_json_file)


# -----------------------------------------------------------------------------
# -- Grasshopper Interface


class GHCompo_CalculateADORBCost(object):
    """GHCompo Interface: HB-REVIVE - Calculate ADORB Costs."""

    def __init__(self, _IGH, _save_file_name, _save_dir, _hb_model, _calculate_ADORB, *args, **kwargs):
        # type: (gh_io.IGH, str | None, str | None, Model, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self._save_filename = _save_file_name
        self.save_dir = _save_dir or os.path.join(hb_folders.default_simulation_folder, "REVIVE")
        self.hb_model = _hb_model
        self.calculate_ADORB = _calculate_ADORB

    def give_user_warnings(self, _stdout):
        # type: (bytes) -> None
        """Give user warnings if any."""
        for line in str(_stdout).split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

    @property
    def save_filename(self):
        # type: () -> str
        """Return the full output filename (without extension)."""
        if self._save_filename:
            return self._save_filename
        else:
            if self.hb_model.display_name:
                return self.hb_model.display_name
            else:
                return "unnamed"

    @property
    def csv_output_file_path(self):
        # type: () -> str
        """Return the full output CSV file path."""
        return os.path.join(self.save_dir, "{}.csv".format(self.save_filename))

    @property
    def hbjson_output_file_path(self):
        # type: () -> str
        """Return the full output HBJSON file path."""
        return os.path.join(self.save_dir, "{}.hbjson".format(self.save_filename))

    def run(self):
        # type: () -> tuple[bytes | None, bytes | None, str | None]
        print("Running ADORB cost calculation...")
        if not self.calculate_ADORB or not self.hb_model:
            return (None, None, None)

        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

        with model_as_json_file(self.hb_model, self.hbjson_output_file_path) as hb_json_filepath:
            results_csv_file_path, stdout, stderr = run_ADORB_calculator(
                _hbjson_filepath=hb_json_filepath,
                _results_file_path=self.csv_output_file_path,
            )
            self.give_user_warnings(stdout)
            print("ADORB costs output to: {}".format(self.csv_output_file_path))

        return stdout, stderr, results_csv_file_path