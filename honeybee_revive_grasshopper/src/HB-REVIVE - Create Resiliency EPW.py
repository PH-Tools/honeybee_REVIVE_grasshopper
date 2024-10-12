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
Create a modified EPW Weather file which will be used for the Phius-REVIVE 'Resiliency'
simulations. This modified EPW will has adjustments maded to the outdoor dry-bub air
temperature and the outdoor air dew-point temperature in order to create a more 'stressful'
climate for the building.
-
EM October 12, 2024
    Args:
        _epw_file: The original EPW weather file to use as the base.

        _stat_file: The original STAT file to use as the base.

        _folder_: (Optional) An optional folder location to store the new EPW file in.
            If none is passed, the default LBT Weather folder will be used. 

        _winter_10yr_dry_bulb_temp: The 10-year extreme (min) Dry-Bulb Air Temp. Use the 
            ashrae-meteo.info website to find these "n-Year Return Period Values of Extreme Temp."

        _winter_10yr_dew_point_temp: The 10-year extreme (min) Dew-Point Air Temp. Use the 
            ashrae-meteo.info website to find these "n-Year Return Period Values of Extreme Temp."

        _summer_20yr_dry_bulb_temp: The 20-year extreme (max) Dry-Bulb Air Temp. Use the 
            ashrae-meteo.info website to find these "n-Year Return Period Values of Extreme Temp."

        _summer_20yr_dew_point_temp: The 20-year extreme (max) Dew-Point Air Temp. Use the 
            ashrae-meteo.info website to find these "n-Year Return Period Values of Extreme Temp."

        _run: Set to 'True' to run the EPW editor.

    Returns:

        epw_file_: The new EPW weather file with values modified to make it more 'stressul' 
            when used during the Phius-REVIVE Resiliency simulations.
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
ghenv.Component.Name = "HB-REVIVE - Create Resiliency EPW"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.resiliency import create_epw as gh_compo_io
    reload(gh_compo_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateResiliencyEPWFile(
        IGH,
        _epw_file,
        _stat_file,
        _folder_, 
        _winter_10yr_dry_bulb_temp,
        _winter_10yr_dew_point_temp,
        _summer_20yr_dry_bulb_temp,
        _summer_20yr_dew_point_temp,
        _run,
)
epw_file_ = gh_compo_interface.run()