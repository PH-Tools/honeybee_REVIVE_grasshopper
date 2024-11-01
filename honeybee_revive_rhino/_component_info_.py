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
    # -- 01 MODEL
    "HB-REVIVE - Set Model Properties": {
        "NickName": "Set Model Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Create CO2 Reduction Measure": {
        "NickName": "Create CO2 Reduction Measure",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Set REVIVE Material Properties": {
        "NickName": "Set REVIVE Material Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Add CO2 Reduction Measures to Model": {
        "NickName": "Add CO2 Reduction Measures to Model",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Set REVIVE Appliance Properties": {
        "NickName": "Set REVIVE Appliance Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Add REVIVE Appliances to Rooms": {
        "NickName": "Add REVIVE Appliances to Rooms",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Create REVIVE Appliance": {
        "NickName": "Create REVIVE Appliance",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Set REVIVE Room Lighting Properties": {
        "NickName": "Set REVIVE Room Lighting Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Set REVIVE Lighting Program Properties": {
        "NickName": "Set REVIVE Lighting Program Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Set REVIVE PV-Shade Properties": {
        "NickName": "Set REVIVE PV-Shade Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Create REVIVE HVAC Equipment Properties": {
        "NickName": "Create REVIVE HVAC Equipment Properties",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Add REVIVE HVAC Equipment Properties to Rooms": {
        "NickName": "Add REVIVE HVAC Equipment Properties to Rooms",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- 03 STANDARDS
    "HB-REVIVE - Load REVIVE Program from Standards": {
        "NickName": "Load REVIVE Program from Standards",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Create REVIVE Residential Program": {
        "NickName": "Create REVIVE Residential Program",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Load REVIVE Schedules from Standards": {
        "NickName": "Load REVIVE Schedules from Standards",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Load REVIVE Appliance from Standards Library": {
        "NickName": "Load REVIVE Appliance from Standards Library",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HB-REVIVE - Load REVIVE CO2-Measures from Standards Library": {
        "NickName": "Load REVIVE CO2-Measures from Standards Library",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- 05 ADORB
    "HB-REVIVE - Calculate ADORB Costs": {
        "NickName": "Calculate ADORB Costs",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HB-REVIVE - Set ADORB Simulation Output Variables": {
        "NickName": "Set ADORB Simulation Output Variables",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- 06 RESILIENCY
    "HB-REVIVE - Create Resiliency EPW": {
        "NickName": "Create Resiliency EPW",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HB-REVIVE - Calculate Dew-Point Temp": {
        "NickName": "Calculate Dew-Point Temp",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HB-REVIVE - Set Resiliency Program": {
        "NickName": "Set Resiliency Program",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HB-REVIVE - Set Resiliency Simulation Output Variables": {
        "NickName": "Set Resiliency Simulation Output Variables",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HB-REVIVE - Generate Winter Resiliency Outputs": {
        "NickName": "Generate Winter Resiliency Outputs",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HB-REVIVE - Generate Summer Resiliency Outputs": {
        "NickName": "Generate Summer Resiliency Outputs",
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
