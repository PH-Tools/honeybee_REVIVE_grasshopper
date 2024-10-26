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
............
-
EM October 26, 2024
    Args:
        _folder_: (Optional) An optional path to a folder to save the graphs 
            to. If none is provided, the default Ladbybug Tools folder will be 
            used as the save folder.

        _sql: The SQL file path from the Honeybee-Energy 'HB Model to OSM' component. 

    Returns:
        winter_SET_hours_below_12C_: [LIMIT=120] The Degree-Hours below 12.2C [54F] for
            each zone during the analysis period.

        winter_SET_hours_below_2C_: [LIMIT=0] The Degree-Hours below 2.2C [26F] for
            each zone during the analysis period.

        output_: The path to the output files.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))

try:
    from honeybee_revive_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_revive_rhino:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_revive_rhino._component_info_
reload(honeybee_revive_rhino._component_info_)
ghenv.Component.Name = "HB-REVIVE - Generate Winter Resiliency Outputs"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.resiliency import generate_winter_output as gh_compo_io
    reload(gh_compo_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_ResiliencyWinterOutput(
        IGH,
        _sql,
        _folder_,
)
(   
    winter_SET_hours_below_12C_,
    winter_SET_hours_below_2C_,
    output_,
) = gh_compo_interface.run()