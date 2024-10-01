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
    from honeybee_revive.grid_region import GridRegion
    from honeybee_revive.national_emissions import NationalEmissionsFactors
    from honeybee_revive_standards import cambium_factors, national_emission_factors
    from honeybee_revive_standards.cambium_factors._load_grid_region import load_grid_region_from_json_file
    from honeybee_revive_standards.national_emission_factors._load_national_emissions import (
        load_national_emissions_from_json_file,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive_standards:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_SetModelProperties(object):

    def __init__(
        self,
        _IGH,
        _country_name,
        _cambium_grid_region,
        analysis_duration,
        envelope_labor_cost_fraction,
        _hb_model,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, str, int, float, Model, list, dict) -> None
        self.IGH = _IGH
        self.country_name = _country_name
        self.cambium_grid_region = _cambium_grid_region
        self.hb_model = _hb_model
        self.analysis_duration = analysis_duration or 50
        self.envelope_labor_cost_fraction = envelope_labor_cost_fraction or 0.4

    def get_national_emissions_factor(self):
        # type: () -> NationalEmissionsFactors | None
        """Get the National Emissions Factors for the country."""

        if not self.country_name:
            return None

        emissions_factor_location = os.path.dirname(national_emission_factors.__file__)
        emissions_factor_json_file = os.path.join(emissions_factor_location, "rv2024_national_emissions.json")
        emissions_factor_dict = load_national_emissions_from_json_file(emissions_factor_json_file)

        try:
            national_emissions_factors = emissions_factor_dict[self.country_name]
        except KeyError:
            msg = "Failed to find National Emissions Factors for: {} in the standards library: {}".format(
                self.country_name, emissions_factor_json_file
            )
            raise ValueError(msg)

        return national_emissions_factors

    def get_grid_region(self):
        # type: () -> GridRegion | None
        """Load the GridRegion Object for the model."""

        if not self.cambium_grid_region:
            return None

        # TODO: Add some sort of Caching so we don't need to load the entire 10 MB JSON file every time

        if self.cambium_grid_region.endswith(".json"):
            # The user passed in a file-path, so just use that one.
            return load_grid_region_from_json_file(self.cambium_grid_region)
        else:
            # The user passed in a GridRegion name, so try and find the file in the 'Standards' and load it
            search_name = "{}.json".format(self.cambium_grid_region)

            # Search through all the files in 'honeybee_revive_standards.cambium_factors' for the 'search_name'
            for root, dirs, files in os.walk(os.path.dirname(cambium_factors.__file__)):
                if search_name in files:
                    return load_grid_region_from_json_file(os.path.join(root, search_name))
            else:
                raise ValueError(
                    "Failed to find a Grid-Region JSON file named: {} in Honeybee-Revive Standards: {}".format(
                        self.cambium_grid_region, cambium_factors.__file__
                    )
                )

    def run(self):
        # type: () -> Model | None

        if not self.hb_model:
            return None

        new_model = self.hb_model.duplicate()
        og_model_prop = getattr(self.hb_model.properties, "revive")  # type: ModelReviveProperties
        new_model_prop = getattr(new_model.properties, "revive")  # type: ModelReviveProperties
        new_model_prop.grid_region = self.get_grid_region() or og_model_prop.grid_region
        new_model_prop.national_emissions_factors = (
            self.get_national_emissions_factor() or og_model_prop.national_emissions_factors
        )
        new_model_prop.analysis_duration = self.analysis_duration
        new_model_prop.envelope_labor_cost_fraction = self.envelope_labor_cost_fraction

        return new_model
