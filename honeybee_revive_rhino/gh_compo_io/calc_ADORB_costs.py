# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HB-REVIVE - Calculate ADORB Cost."""

import json
import os
import sys
from contextlib import contextmanager

try:
    from typing import Any, Generator, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_revive_rhino.run import calculate_HB_model_ADORB_cost
except ImportError as e:
    raise ImportError("\nFailed to import PHX:\n\t{}".format(e))


def using_python_2():
    # type: () -> bool
    """Returns True if the current Python interpreter is Python 2."""
    return sys.version_info < (3, 0)


def write_hb_model_to_json_file(_hb_model):
    # type: (Model) -> str
    """Write out a HB Model to a JSON file.

    Adapted from the Grasshopper "Honeybee - HB Dump Objects" Component
    """
    # -- Setup the file path
    file_name = "{}.hbjson".format(_hb_model.display_name)
    folder = folders.default_simulation_folder
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
    if using_python_2():
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
            saved_file_dir, saved_file_name, stdout, stderr = calculate_HB_model_ADORB_cost(
                _hbjson_filepath=hb_json_filepath,
                _results_file_name=os.path.join(os.path.dirname(__file__), "run.txt"),
                _results_folder=folders.default_simulation_folder,
            )
            self.give_user_warnings(stdout)
            print("ADORB costs output to: {}  |  {}".format(saved_file_dir, saved_file_name))

        return stdout, stderr
