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
Calculate the Phius-REVIVE ADORB costs for the Honeybee-Model.
-
EM September 25, 2024
    Args:

        _name_: (str) An optional variant name to be used for all of the output 
            files. If none is passed, will use the Model's display_name

        _folder_: (str) An optional path to the folder you would like to save
            the output files to. If none is passed, will use the default Honeybee
            simulation path:
            - MacOS > ./Users/{you}/simulatiion/...
            - Windows > someplace...

        _sql_path: (str) The path to the EnergyPlus results SQL file generated by Honeybee-Energy.

        _hb_model: (Model) The Honeybee-Model to calculate the Phius REVIVE ADORB Costs for.
        
        _run: (bool) Set to True to run the calculation.
            
    Returns:
        ADORB_Costs_: .....
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
ghenv.Component.Name = "HB-REVIVE - Calculate ADORB Costs"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io import calc_ADORB_costs as gh_compo_io
    reload(gh_compo_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CalculateADORBCost(
        DEV,
        IGH,
        _name_, 
        _folder_,
        _sql_path,
        _hb_model,
        _run,
)
ADORB_costs_ = gh_compo_interface.run()