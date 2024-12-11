# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Generate ADORB Output Graphs."""

import os

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


def run_ADORB_grapher(_csv_filepath, _output_file_path, *args, **kwargs):
    # type: (str, str, list, dict) -> tuple[bytes, bytes, str]
    """Using Ladybug's Python-3 interpreter: read in an ADORB-Cost CSV file and graph the values.

    ### Arguments:
        * _csv_filepath: File path to the ADORB Cost CSV file.
        * _output_file_path: The file path for the output graph.
        * args: Additional arguments to pass to the subprocess. (ignored)
        * kwargs: Additional keyword arguments to pass to the subprocess. (ignored)

    ### Returns:
        * tuple
            - [0] (bytes): The stdout from the subprocess.
            - [1] (bytes): The stderr from the subprocess.
            - [2] (str): The path to the output results file.
    """

    # -- Specify the path to the actual subprocess python-3 script to run
    py3_script_filepath = os.path.join(
        hb_folders.python_package_path, "ph_adorb", "run", "generate_ADORB_cost_graph.py"
    )

    # -- check the file paths
    assert os.path.isfile(_csv_filepath), "No ADORB CSV file found at {}.".format(_csv_filepath)
    assert os.path.isfile(py3_script_filepath), "No Python file to run found at: {}".format(py3_script_filepath)

    # -------------------------------------------------------------------------
    # -- Read in the HBJSON, convert to WUFI XML
    print("Using Python-3 interpreter: '{}'".format(hb_folders.python_exe_path))
    print("Running Python-3 script: '{}'".format(py3_script_filepath))
    print("With the HBJSON file: '{}'".format(_csv_filepath))
    commands = [
        hb_folders.python_exe_path,  # -- The interpreter to use
        py3_script_filepath,  # --------- The script to run
        _csv_filepath,  # --------------- The CSV file to graph
        _output_file_path,  # ----------- The filename of the graph output
    ]
    stdout, stderr = run_subprocess(commands)

    # -------------------------------------------------------------------------
    # -- return the dir and filename of the xml created
    return stdout, stderr, _output_file_path


# -----------------------------------------------------------------------------
# -- Grasshopper Interface


class GHCompo_GenerateADORBGraphs(object):
    """GHCompo Interface: HB-REVIVE - Generate ADORB Output Graphs."""

    def __init__(self, _DEBUG, _IGH, _csv, _save_dir, *args, **kwargs):
        # type: (bool, gh_io.IGH, str, str, list, dict) -> None
        self.DEBUG = _DEBUG
        self.IGH = _IGH
        self.csv = _csv
        self.save_dir = _save_dir or os.path.join(hb_folders.default_simulation_folder, "REVIVE")

    def give_user_warnings(self, _stdout):
        # type: (bytes) -> None
        """Give user warnings if any."""
        for line in str(_stdout).split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

    @property
    def ready(self):
        if not self.csv:
            self.IGH.warning("Input an ADORB Cost CSV File to graph.")
            return False

        if not os.path.isfile(self.csv):
            msg = "No ADORB Cost CSV file found at: {}".format(self.csv)
            self.IGH.error(msg)
            return False

        if not os.path.isdir(self.save_dir):
            msg = "Creating folder: {}".format(self.save_dir)
            self.IGH.remark(msg)
            print(msg)
            os.makedirs(self.save_dir)

        return True

    @property
    def save_file(self):
        filename_without_ext = os.path.splitext(os.path.basename(self.csv))[0]
        return os.path.join(self.save_dir, "{}.html".format(filename_without_ext))

    def run(self):
        if not self.ready:
            return None

        print("Running ADORB cost calculation...")
        stdout, stderr, output_folder = run_ADORB_grapher(self.csv, self.save_file)
        self.give_user_warnings(stdout)

        if stderr:
            print(stderr)
            self.IGH.error(stderr)
            return None

        return output_folder
