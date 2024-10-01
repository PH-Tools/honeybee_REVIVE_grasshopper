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
Create a new Phius-REVIVE-HVAC-Equipment-Properties item which can be added to a Honeybee-Room.
Note that this equipment is ONLY for keeping track of the relevant Phius-REVIVE
properties and does NOT add any actual equipment to the Honeybee-Rooms. Use the normal 
Honeybee-Energy components to configure the actual equipment objects on the roonms.
-
EM October 1, 2024
    Args:
        _name: (str) A name for the piece of REVIVE-HVAC-Equipment-Properties.

        _cost: (float) The total purchase-cost of the Appliance.

        _labor_fraction: (float) A number between 0 and 1.0 representing the percentage
            of the appliance cost related to labor, as opposed to material. 

        _lifetime_years: (float) The total number of years the appliance will last
            before it needs to be completely replaced. 

    Returns:
        hvac_equipment_properties_: (Process) The Honeybee-REVIVE-HVAC-Properties which can be added
            a Honeybee-Room.
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
ghenv.Component.Name = "HB-REVIVE - Create REVIVE HVAC Equipment Properties"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.equipment import hvac_create_properties as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateReviveHvacEquipmentProperties(
        IGH,
        _name,
        _cost,
        _labor_fraction,
        _lifetime_years,
)
hvac_equipment_properties_ = gh_compo_interface.run()
print hvac_equipment_properties_