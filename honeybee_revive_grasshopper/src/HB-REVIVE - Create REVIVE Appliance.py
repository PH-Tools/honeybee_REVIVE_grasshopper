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
Create a new Honeybee-REVIVE Appliance which can be added to one or more Honeybee-Rooms.
-
EM October 1, 2024
    Args:
        _name_: (str) Text to set the name for the Appliance and to be incorporated into a
            unique Appliance identifier. If None, a unique name will be
            generated.
        
        _watts: (float) A number for the process load power in Watts.
        
        _schedule: A fractional schedule for the use of the process over the course of
            the year. The fractional values will get multiplied by the _watts
            to yield a complete process load profile.
        
        _fuel_type: (str) Text to denote the type of fuel consumed by the Appliance. Using the
            "None" type indicates that no end uses will be associated with the
            Appliance, only the zone gains. Choose from the following.
                * Electricity
                * NaturalGas
                * Propane
                * FuelOilNo1
                * FuelOilNo2
                * Diesel
                * Gasoline
                * Coal
                * Steam
                * DistrictHeating
                * DistrictCooling
                * OtherFuel1
                * OtherFuel2
                * None
        
        use_category_: Text to indicate the end-use subcategory, which will identify
            the appliance load in the EUI output. For example, “Cooking”,
            “Clothes Drying”, etc. (Default: General).
        
        radiant_fract_: A number between 0 and 1 for the fraction of the total
            appliance load given off as long wave radiant heat. (Default: 0).
        
        latent_fract_: A number between 0 and 1 for the fraction of the total
            appliance load that is latent (as opposed to sensible). (Default: 0).
        
        lost_fract_: A number between 0 and 1 for the fraction of the total
            appliance load that is lost outside of the zone and the HVAC system.
            Typically, this is used to represent heat that is exhausted directly
            out of a zone (as you would for a stove). (Default: 0).

    Returns:
        appliance_: (Process) The new Honeybee-REVIVE Appliance which can be added
            to one or more Honeybee-Rooms.
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
ghenv.Component.Name = "HB-REVIVE - Create REVIVE Appliance"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.equipment import appliances_create as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateReviveAppliance(
        IGH,
        _name_,
        _watts,
        _schedule,
        _fuel_type,
        use_category_,
        radiant_fract_,
        latent_fract_,
        lost_fract_,
)
appliance_ = gh_compo_interface.run()
print appliance_