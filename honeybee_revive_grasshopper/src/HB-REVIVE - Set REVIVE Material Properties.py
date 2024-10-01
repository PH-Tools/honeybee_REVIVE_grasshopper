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
Assing Phius-REVIVE material attributes related to CO2 emissions and cost. This 
component will work for any Honeybee-Energy Material, including:
- HB Opaque Material
- HB Opaque Material No Mass
- HB Vegetation Material
- HB Glass Material
- HB Window Gap Material
- HB Custom Window Gap Material
- HB Window Material
- HB Frame Material
- HB Shade Material
- HB Blind Material
-
EM October 1, 2024
    Args:
        _hb_material: (Honeybee-Energy-Material) The Honeybee-Energy Material to 
            add the new REVIVE properties to.

        _k_CO2_per_m2: (float) The KG-CO2/m2 emitted during the creation of the material. 

        _cost_per_m2: (float) The cost per m2 of the material.

        _labor_fraction: (float) The portion (%) of the material cost/CO2 which is 
            related to the labor, as opposed to the material itself.

        _lifetime_years: (int) The number of years which the material will last for.

    Returns:
        hb_material_: (Honeybee-Energy-object) The Honeybee-Energy Material with the new 
            REVIVE properties set.
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
ghenv.Component.Name = "HB-REVIVE - Set REVIVE Material Properties"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.envelope import set_material_properties as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetMaterialProperties(
        IGH,
        _hb_material,
        _kg_CO2_per_m2,
        _cost_per_m2,
        _labor_fraction,
        _lifetime_years,
)
hb_material_ = gh_compo_interface.run()
if hb_material_:
    print(hb_material_.properties.revive)
