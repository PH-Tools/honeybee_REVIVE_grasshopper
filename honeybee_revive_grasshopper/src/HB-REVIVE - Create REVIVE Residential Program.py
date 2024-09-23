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
Create a new Phius-REVIVE Residential Program which can be applied to one or more 
Honeybee-Rooms. This Phius Program will determine the lighting, MEL, and occupancy based on the 
number of bedrooms, the number of total dwelling units, and the total iCFA (interior conditioned
floor area). This component takes in a base-program and will modify the lighting, MEL, and occupancy
loads only. For most Phius-REVIVE projects, you should use the default program from the REVIVE
standards library. You can load this default program using the "Load REVIVE Program from Standards"
grasshopper component, and pass it in as the _base_program.
-
For more information on how these values are calculated, see the Phius Manual(s) or:
https://codes.iccsafe.org/content/RESNET3012014P1/4-home-energy-rating-calculation-procedures-
-
EM September 23, 2024
    Args:
        _total_icfa: (float) The total Interio-Conditioned-Floor-Area of the entire building
            area being simulated.

        _total_number_dwellings: (int) The total number of dwelling units in the entire building
            area being simulated.

        _total_number_bedrooms: (int) The total number of bedrooms in the entire building
            area being simulated.

        _base_program: (ProgramType) A base program of loads and schedules to use as the 
            starting point for the new Phius-REVIVE Residential Program. In most cases you
            should use the default program provided in the Honeybee-REVIVE-Standards, but you 
            can also provided your own custom schedule to use as the base.

    Returns:
        hb_energy_program_: (ProgramType | None) The Honeybee-Energy Program with the Lighting, 
            MEL, and occupancy values assigned baseed on the attributes provided. 
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
ghenv.Component.Name = "HB-REVIVE - Create REVIVE Residential Program"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io import create_revive_residential_program as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateReviveResidentialProgram(
        IGH,
        _total_icfa,
        _total_number_dwellings,
        _total_number_bedrooms,
        _base_program,
)
hb_energy_program_ = gh_compo_interface.run()
print hb_energy_program_