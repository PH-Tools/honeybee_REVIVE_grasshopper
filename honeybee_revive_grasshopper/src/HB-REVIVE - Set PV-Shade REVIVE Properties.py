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
Add Phius-REVIVE properties to one or more Honeybee-Shade objects which have 
PV (Photovoltaic) panels on them. Note that you should use the Honeybee-Energy
'HB Photovoltaic Properties' component to set up the basic PV panel attributes
FIRST before using this componet to set the Phius-REVIVE properties.
-
EM September 21, 2024
    Args:
        _cost: (float) The total cost of the PV

        _labor_fraction: (float) The fraction of the PV cost associated with labor,
            as opposed to material.

        _lifetime_years: (float) The lifetime (in years) of the PV

        _hb_shades: (list[Shade]) A list of Honeybee-Energy Shade objects which 
            have PV-Modules added to them.

    Returns:
        hb_shades_: (list[Shade]) The Honeybee-Energy-Shade objects with their 
            Phius-REVIVE properties set. These Shades can be added to a Honeybee-Model.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_revive_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_revive_rhino:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_revive_rhino._component_info_
reload(honeybee_revive_rhino._component_info_)
ghenv.Component.Name = "HB-REVIVE - Set PV-Shade REVIVE Properties"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io import set_pv_shade_properties as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetPvShadeProperties(
        IGH,
        _cost,
        _labor_fraction,
        _lifetime_years,
        _hb_shades,
)
hb_shades_ = gh_compo_interface.run()