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
Create a new ADORB Fuel type which will be used during the ADORB Calculations.
-
EM November 22, 2024
    Args:
        _fuel_type: Input either:
1-Electricity
2-Natural Gas

        _purchase_price_per_kWH: The cost of a purchased kWH of energy.

        _sale_price_per_kWH: (Optional) Default=0 The sale-price of a kWH of energy. Generally 
            only relevant to electricity which is produced from onsite renewables. 

        _annual_base_cost: (Optional) Default=0 Any additional annual costs for hookups or 
            other fees in addition to the per-kWH costs.

    Returns:
        fuel_: The new fuel type which can be added to 'HB-REVIVE Set Model Properties' which
            will be used during the ADORB calculations.
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
ghenv.Component.Name = "HB-REVIVE - ADORB Fuel Type"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.adorb import create_fuel as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateADORBFuelType(
        DEV,
        IGH,
        _fuel_type,
        _purchase_price_per_kWH,
        _sale_price_per_kWH,
        _annual_base_cost,
)
fuel_ = gh_compo_interface.run()
preview.object_preview(fuel_)