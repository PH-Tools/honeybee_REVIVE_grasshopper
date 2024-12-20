#
# Honeybee-REVIVE: A Plugin for calculating Phius REVIVE using LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2024, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
# Honeybee-REVIVE is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee-REVIVE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# For a copy of the GNU General Public License
# see <https://github.com/PH-Tools/honeybee_revive/blob/main/LICENSE>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
Set the Phius-REVIVE ADORB calculation parameters for the Honeybee-Model.
-
EM November 22, 2024
    Args:
        _country_name: (str) The name of the Country the model is located in.

        _cambium_grid_region: (str) Pass in either the name of the Cambium Grid-Region you 
            would like to use (ie: 'AZNMc', etc..) or the filepath to a Cambium Grid-Region
            JSON file that you would like to use for the REVIVE ADORB analysis.
            
        _analysis_duration: (int) The number of years to run the ADORB analysis for.

        _envelope_labor_cost_fraction: (float) The percentage of the envelope cost
            which is related to labor, as opposed to materials.

        _hb_model: (Model) The Honeybee Model to set the REVIVE properties on.

    Returns:
        hb_model_: (Model) The Honeybee Model with the REVIVE properties set.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from ph_gh_component_io import gh_io, preview
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))

try:
    from honeybee_revive_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_revive_rhino:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_revive_rhino._component_info_
reload(honeybee_revive_rhino._component_info_)
ghenv.Component.Name = "HB-REVIVE - Set Model Properties"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.model import set_model_properties as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetModelProperties(
        IGH,
        _country_name,
        _cambium_grid_region,
        _analysis_duration,
        _envelope_labor_cost_fraction,
        _fuels,
        _hb_model,
)
hb_model_ = gh_compo_interface.run()
if hb_model_:
    preview.object_preview(hb_model_.properties.revive)