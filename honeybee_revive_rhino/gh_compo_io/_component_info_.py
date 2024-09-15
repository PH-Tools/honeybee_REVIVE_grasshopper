# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Names and meta-data for all the Honeybee-PH Grasshopper Components.
These are called when the component is instantiated within the Grasshopper canvas.
"""

RELEASE_VERSION = "Honeybee-REVIVE v0.0.01"
CATEGORY = "HB-REVIVE"
SUB_CATEGORIES = {
    0: "00 | Utils",
    1: "01 | Model",
    2: "02 | ADORB",
}
COMPONENT_PARAMS = {
    # -- 02 ADORB
    "HB-REVIVE - Calculate ADORB Costs": {
        "NickName": "Calculate ADORB Costs",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
}


class ComponentNameError(Exception):
    def __init__(self, _name, error):
        self.message = 'Error: Cannot get Component Params for: "{}"'.format(_name)
        print(error)
        super(ComponentNameError, self).__init__(self.message)


def turn_off_old_tag(ghenv):
    """Turn off the old tag that displays on GHPython components.
    Copied from 'ladybug-rhino.grasshopper.turn_off_old_tag()'

    Arguments:
    __________
        * ghenv: The Grasshopper Component 'ghenv' variable.

    Returns:
    --------
        * None:
    """
    try:  # try to turn off the OLD tag on the component
        ghenv.Component.ToggleObsolete(False)
    except Exception:
        pass  # older version of Rhino that does not have the Obsolete method


def set_component_params(ghenv, dev=False):
    # type (ghenv, Optional[str | bool]) -> bool
    """
    Sets the visible attributes of the Grasshopper Component (Name, Date, etc..)

    Arguments:
    __________
        * ghenv: The Grasshopper Component 'ghenv' variable.
        * dev: (str | bool) Default=False. If False, will use the RELEASE_VERSION value as the
            'message' shown on the bottom of the component in the Grasshopper scene.
            If a string is passed in, will use that for the 'message' shown instead.

    Returns:
    --------
        * None:
    """

    compo_name = ghenv.Component.Name
    try:
        sub_cat_num = COMPONENT_PARAMS.get(compo_name, {}).get("SubCategory", 1)
        sub_cat_name = SUB_CATEGORIES.get(sub_cat_num)
    except Exception as e:
        raise ComponentNameError(compo_name, e)

    # ------ Set the visible message
    if dev:
        msg = "DEV | {}".format(str(dev))
    else:
        msg = COMPONENT_PARAMS.get(compo_name, {}).get("Message")

    ghenv.Component.Message = msg

    # ------ Set the other stuff
    ghenv.Component.NickName = COMPONENT_PARAMS.get(compo_name, {}).get("NickName")
    ghenv.Component.Category = CATEGORY
    ghenv.Component.SubCategory = sub_cat_name
    ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
    turn_off_old_tag(ghenv)  # For Rhino 8

    return dev