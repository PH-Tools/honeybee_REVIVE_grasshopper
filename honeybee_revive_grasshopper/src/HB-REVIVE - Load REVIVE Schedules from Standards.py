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
Load the Honeybee-Energy Schedules from the Phius-REVIVE-2024 Standards Library. This 
Schedule can be assigned to one or more Honeybee-Rooms.
-
EM November 1, 2024
    Args:
        _standards_path_: (str | None) OPTIONAL path to the Phius-REVIVE-2024 Standards Path 
            that you would like to use. If None is provided, the default standards 
            directory location will be used.

        _schedule_names_: (str | None) OPTIONAL names for the Phius-REVIVE-2024 Schedules
            to load from the Standards directory. Note that if No name is provided, the 
            component will load all of the Phius REVIVE Schedules.

    Returns:
        schedules_: (ProgramType | None) The Honeybee-Energy Schedules found in
            the Phius REVIVE 2024 Standards directory, or None if not found. 
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
ghenv.Component.Name = "HB-REVIVE - Load REVIVE Schedules from Standards"
DEV = honeybee_revive_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_revive_rhino.gh_compo_io.standards import load_schedules_from_standards as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_LoadSchedulesFromStandards(
        IGH,
        _standards_path_,
)
all_schedules = gh_compo_interface.run()
for schedule in all_schedules:
    print schedule.display_name


if _schedule_names_:
    shcd_names = [s.upper().strip() for s in _schedule_names_]
    schedules_ = [s for s in all_schedules if s.display_name.upper().strip() in shcd_names]
else:
    schedules_ = all_schedules