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
Create a new Phius-REVIVE CO2 Reduction Measure which can be applied to a
Honeybee Model. Note that a Honeybee Model can have several measures applied.
-
EM September 18, 2024
    Args:
        _name: (str) The name to give to the CO2-Reduction-Measure

        _measure_type: (CO2ReductionMeasureType) Input either:
            "1-PERFORMANCE"
            "2-NON_PERFORMANCE"
            
        _year: (int) The year

        _cost: (float) The cost of the measure.

        _kg_CO2: (float) The KG of CO2e reduced by the measure.

        _country_name: (str) The name of the country.

        _labor_fraction: (float) The percentage of the measure which is 
            related to labor, as opposed to material.

    Returns:
        measure_: (CO2ReductionMeasure) The new CO2-Reduction-Measure which can 
            be added to a Honeybee-Model.
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
ghenv.Component.Name = "HB-REVIVE - Create CO2 Reduction Measure"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io import create_CO2_measure as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateCO2ReductionMeasure(
        IGH,
        _name,
        _measure_type,
        _year,
        _cost,
        _kg_CO2,
        _country_name,
        _labor_fraction,
)
measure_ = gh_compo_interface.run()
print(measure_)
