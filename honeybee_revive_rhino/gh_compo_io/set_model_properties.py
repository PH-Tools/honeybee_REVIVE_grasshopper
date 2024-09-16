# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Set Model Properties."""

import os

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_revive.properties.model import ModelReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))

try:
    from honeybee_revive_standards import cambium_factors
    from honeybee_revive_standards.cambium_factors._load_grid_region import load_grid_region_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive_standards:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")


class GHCompo_SetModelProperties(object):

    def __init__(self, _IGH, _cambium_grid_region, _hb_model):
        # type: (gh_io.IGH, str, Model) -> None
        self.IGH = _IGH
        self.cambium_grid_region = _cambium_grid_region
        self.hb_model = _hb_model

    def run(self):
        # type: () -> Model | None

        if not self.hb_model:
            return None

        new_model = self.hb_model.duplicate()
        model_prop = getattr(new_model.properties, "revive")  # type: ModelReviveProperties

        # --------------------------------------------------------------------------------------------------------------
        # -- Set the Cambium Grid Region Data
        # TODO: Add some sort of Caching so we don't need to load the entire 10 MB JSON file every time
        if self.cambium_grid_region.endswith(".json"):
            # The user passed in a file-path, so just use that one.
            model_prop.grid_region = load_grid_region_from_json_file(self.cambium_grid_region)
        else:
            # The user passed in a GridRegion name, so try and find the file in the 'Standards' and load it
            search_name = "{}.json".format(self.cambium_grid_region)

            # Search through all the files in 'honeybee_revive_standards.cambium_factors' for the 'search_name'
            for root, dirs, files in os.walk(os.path.dirname(cambium_factors.__file__)):
                if search_name in files:
                    model_prop.grid_region = load_grid_region_from_json_file(os.path.join(root, search_name))
                    break
            else:
                raise ValueError(
                    "Failed to find a Grid-Region JSON file named: {} in Honeybee-Revive Standards: {}".format(
                        self.cambium_grid_region, cambium_factors.__file__
                    )
                )

        return new_model
