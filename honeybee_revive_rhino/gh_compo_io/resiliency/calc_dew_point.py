# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Calculate Dew-Point Temp."""

import math

try:
    from ladybug.psychrometrics import dew_point_from_db_rh, rel_humid_from_db_wb
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


class GHCompo_CalculateDewPoint(object):

    elevation = validators.UnitM("elevation")
    dry_bulb_temp = validators.UnitDegreeC("dry_bulb_temp")
    wet_bulb_temp = validators.UnitDegreeC("wet_bulb_temp")

    def __init__(self, _IGH, _elevation, _dry_bulb_temp, _wet_bulb_temp):
        # type: (gh_io.IGH, float, float, float) -> None
        self.IGH = _IGH
        self.elevation = _elevation
        self.dry_bulb_temp = _dry_bulb_temp
        self.wet_bulb_temp = _wet_bulb_temp
        self.air_pressure_Pa = self.air_pressure_from_elevation(self.elevation)

    def air_pressure_from_elevation(self, _elevation):
        # type: (float | None) -> float
        """Get the air pressure (in Pa), based on the elevation (in Meters)."""

        if _elevation is None:
            pressure_Pa_ = 101325.0
        else:
            kPa = 29.921 * math.pow((1 - 6.87535e-06 * _elevation / 0.3048), 5.256) * 3.38650
            pressure_Pa_ = (kPa) * 1000

        print("Pressure: {:,.0f} Pa".format(pressure_Pa_))
        return pressure_Pa_

    @property
    def ready(self):
        # type: () -> bool
        return self.dry_bulb_temp is not None and self.wet_bulb_temp is not None

    def run(self):
        # type: () -> tuple[float, float, float, float] | tuple[None, None, None, None]
        if not self.ready:
            return (None, None, None, None)

        rh = rel_humid_from_db_wb(self.dry_bulb_temp, self.wet_bulb_temp, self.air_pressure_Pa)  # type: ignore
        print("RH: {:.1f} %".format(rh))

        dew_point = dew_point_from_db_rh(self.dry_bulb_temp, rh)
        print("DP: {:.2f} C".format(dew_point))

        return (self.dry_bulb_temp, dew_point, rh, self.air_pressure_Pa)
