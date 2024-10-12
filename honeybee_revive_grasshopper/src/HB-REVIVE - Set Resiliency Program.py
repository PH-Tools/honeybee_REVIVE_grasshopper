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
Setup a Phius-REVIVE 'Resiliency' Honeybee-Program and apply it to the Rooms. This Program
is uses to simulate a 'grid-outage' event and is used to assess the building against the 
Phius REVIVE Winter and Summer resiliency periods.
- 
This new program will:
- Set the Occupancy Schedule to 'Constant' (full occupancy)
- Turn off all existing Lighting, Process, and Electrical Loads
- Set electrical 'critical' loads to 33W/dwelling (critical loads = 1 fridge)
- Turn off all Heating/Cooling equipment
- Reset the Ventilation flow rates to 5cfm (8.5 m3/h) / person
-
EM October 12, 2024
    Args:
        _hb_obj: (list[Room] | Model) The Honeybee-Rooms or a Honeybee-Model.

        _total_num_dwelling_units: (int) The total number of dwelling units in the building.

        _additional_elec_equip: (Optional) Default=None. Input a list of any additional electric
            equipment which should be operational during the resiliency simulations. This
            would be any 'critical load' items which are powered by battery or other storage
            during a grid-outage event. Note that the standard Phius Resiliency load requires
            33W/dwelling (1 fridge) which is already included by default - so only provide 
            additional items beyond this base load. In most residential cases this should 
            probably be None.

        _program_: (Optional)  Default=None. An optional base program to use when creating the new Phius
            REVIVE Resiliency Program. In none is provided, the default Resiliency Program from
            the Standards library will be used.

    Returns:
        hb_obj_: The Honeybee-Rooms or Honeybee-Model with the new Program applied. 
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
ghenv.Component.Name = "HB-REVIVE - Set Resiliency Program"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    import ph_units
    reload(ph_units)
    from honeybee_revive_rhino.gh_compo_io.resiliency import set_resiliency_program as gh_compo_io
    reload(gh_compo_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetResiliencyProgram(
        IGH,
        _hb_obj,
        _total_num_dwelling_units,
        _additional_elec_equip,
        _program_,
)
hb_obj_, program_ = gh_compo_interface.run()