# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Run a Python Subprocess."""


import os
import subprocess


def run_subprocess(commands):
    # type: (list[str]) -> tuple[bytes, bytes]
    """Run a python subprocess.Popen, using the supplied commands.

    Args:
        commands: A list of the commands to pass to Popen

    Returns:
        tuple:
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
